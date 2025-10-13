import os
import json
from typing import List, Dict, Any, Optional
from django.conf import settings
from django.db.models import Q
from .models import Property, PropertyImage, User, ChatSession, ChatMessage
import openai
import google.generativeai as genai

class PropertySearchService:
    """Service for searching properties based on user queries"""
    
    @staticmethod
    def search_properties(query: str, limit: int = 5, current_user: Optional[User] = None) -> List[Property]:
        """
        Search properties using text search across relevant fields
        """
        # Create search terms from query
        search_terms = query.lower().split()
        
        # Build Q objects for different fields
        q_objects = Q()
        
        for term in search_terms:
            q_objects |= (
                Q(title__icontains=term) |
                Q(description__icontains=term) |
                Q(city__icontains=term) |
                Q(state__icontains=term) |
                Q(location__icontains=term) |
                Q(type__icontains=term)
            )
        
        # Search for properties
        queryset = Property.objects.filter(
            q_objects,
            is_verified=True
        )

        # If current user is also a seller, exclude their own listings from results
        if current_user is not None and getattr(current_user, 'is_seller', False):
            queryset = queryset.exclude(seller=current_user)

        properties = queryset.select_related('seller').prefetch_related('images')[:limit]
        
        return list(properties)
    
    @staticmethod
    def search_by_criteria(city: str = None, state: str = None, 
                          property_type: str = None, max_price: float = None,
                          min_price: float = None, limit: int = 5,
                          current_user: Optional[User] = None) -> List[Property]:
        """
        Search properties by specific criteria
        """
        q_objects = Q(is_verified=True)
        
        if city:
            q_objects &= Q(city__icontains=city)
        if state:
            q_objects &= Q(state__icontains=state)
        if property_type:
            q_objects &= Q(type__icontains=property_type)
        if min_price:
            q_objects &= Q(price__gte=min_price)
        if max_price:
            q_objects &= Q(price__lte=max_price)
        
        queryset = Property.objects.filter(q_objects)

        # Exclude current user's own properties if they are a seller
        if current_user is not None and getattr(current_user, 'is_seller', False):
            queryset = queryset.exclude(seller=current_user)

        properties = queryset.select_related('seller').prefetch_related('images')[:limit]
        return list(properties)

class ChatService:
    """Service for handling AI chat interactions"""
    
    def __init__(self):
        self.property_search = PropertySearchService()
        self.use_gemini = bool(settings.GEMINI_API_KEY)
        if self.use_gemini:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            model_name = getattr(settings, 'GEMINI_MODEL_NAME', 'gemini-1.5-flash-latest')
            # normalize a few common aliases
            alias_map = {
                'gemini-1.5-flash': 'gemini-1.5-flash-latest',
                'gemini-1.5-pro': 'gemini-1.5-pro-latest',
                'gemini-2.0-flash': 'gemini-2.0-flash',
            }
            model_name = alias_map.get(model_name, model_name)
            self.gemini_model = genai.GenerativeModel(model_name)
        else:
            self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def create_or_get_session(self, user: User) -> ChatSession:
        """Create a new chat session or get the latest active one"""
        session = ChatSession.objects.filter(
            user=user, 
            is_active=True
        ).order_by('-created_at').first()
        
        if not session:
            session = ChatSession.objects.create(user=user)
        
        return session
    
    def format_property_context(self, properties: List[Property]) -> str:
        """Format properties into context string for LLM"""
        if not properties:
            return "No properties found matching the criteria."
        
        context_parts = []
        for prop in properties:
            # Get first image if available
            first_image = prop.images.first()
            image_info = f" (Image: {first_image.image.name})" if first_image else ""
            
            # Format property details
            prop_info = f"""
Property ID: {prop.id}
Title: {prop.title}
Description: {prop.description}
Type: {prop.type}
Price: ₹{prop.price:,.2f}
Location: {prop.location}, {prop.city}, {prop.state}
Size: {prop.length}x{prop.width} sq ft (if available)
Rooms: {prop.rooms} | Bedrooms: {prop.bedrooms} | Bathrooms: {prop.bathrooms}
Furnished: {'Yes' if prop.furnished else 'No'}
Seller: {prop.seller.first_name} {prop.seller.last_name}
Views: {prop.views}
{image_info}
---"""
            context_parts.append(prop_info)
        
        return "\n".join(context_parts)
    
    def generate_response(self, user_message: str, session: ChatSession) -> Dict[str, Any]:
        """Generate AI response using OpenAI"""
        
        # Search for relevant properties
        properties = self.property_search.search_properties(user_message, current_user=session.user)
        
        # Format property context
        property_context = self.format_property_context(properties)
        
        # Get recent chat history (last 5 messages)
        recent_messages = ChatMessage.objects.filter(
            session=session
        ).order_by('-created_at')[:5]
        
        # Build conversation history
        conversation_history = []
        for msg in reversed(recent_messages):
            role = "user" if msg.message_type == "user" else "assistant"
            conversation_history.append({
                "role": role,
                "content": msg.content
            })
        
        # Add current user message
        conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # System prompt
        system_prompt = f"""You are a helpful real estate assistant for PropKart. 
You help buyers find properties based on their requirements.

Available properties:
{property_context}

Instructions:
1. Answer questions about properties using ONLY the information provided above
2. If you don't have information about something, say "I don't have that information"
3. Always mention Property IDs when referencing specific properties
4. Be helpful and friendly
5. Suggest viewing properties if they match the user's needs
6. If no properties match, suggest different search criteria

Current conversation context: You are helping a buyer find their ideal property."""

        try:
            if self.use_gemini:
                # Gemini expects a single prompt string; combine system + messages
                prompt_parts = [system_prompt]
                for m in conversation_history:
                    prefix = 'User' if m["role"] == 'user' else 'Assistant'
                    prompt_parts.append(f"{prefix}: {m['content']}")
                full_prompt = "\n".join(prompt_parts)
                gemini_resp = self.gemini_model.generate_content(full_prompt)
                ai_response = getattr(gemini_resp, 'text', None) or (
                    gemini_resp.candidates[0].content.parts[0].text if getattr(gemini_resp, 'candidates', None) else ""
                )
            else:
                # OpenAI Chat Completions
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        *conversation_history
                    ],
                    max_tokens=500,
                    temperature=0.7
                )
                ai_response = response.choices[0].message.content
            
            # Extract property IDs from response (simple extraction)
            referenced_property_ids = []
            for prop in properties:
                if str(prop.id) in ai_response:
                    referenced_property_ids.append(prop.id)
            
            return {
                'response': ai_response,
                'referenced_properties': referenced_property_ids,
                'properties_found': len(properties)
            }
            
        except Exception as e:
            return {
                'response': f"I'm sorry, I'm having trouble processing your request right now. Please try again later. Error: {str(e)}",
                'referenced_properties': [],
                'properties_found': 0
            }
    
    def process_message(self, user: User, message: str) -> Dict[str, Any]:
        """Process a user message and return response"""
        
        # Get or create session
        session = self.create_or_get_session(user)
        
        # Save user message
        user_msg = ChatMessage.objects.create(
            session=session,
            message_type='user',
            content=message
        )
        
        # Generate AI response
        ai_response_data = self.generate_response(message, session)
        
        # Save AI response
        ai_msg = ChatMessage.objects.create(
            session=session,
            message_type='assistant',
            content=ai_response_data['response'],
            referenced_properties=ai_response_data['referenced_properties']
        )
        
        return {
            'message_id': ai_msg.id,
            'response': ai_response_data['response'],
            'referenced_properties': ai_response_data['referenced_properties'],
            'properties_found': ai_response_data['properties_found'],
            'session_id': str(session.session_id)
        }
