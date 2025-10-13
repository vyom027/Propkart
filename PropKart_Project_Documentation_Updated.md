 🏠 PropKart - Property Management Platform Documentation

## 🏗 INTRODUCTION

### 1.1 Existing System
Traditional property dealing often relies on fragmented platforms, manual listings, and offline interactions. Many existing systems lack integration between buyers, sellers, and agents, resulting in inefficiencies, limited transparency, and poor user experience. Moreover, legacy platforms may not support scalable architecture or modern security standards.

### 1.2 Need for the New System
With the rapid digitization of real estate, there's a growing demand for a centralized, secure, and user-friendly platform. PropKart addresses this need by offering a modern web-based solution that streamlines property transactions, enhances discoverability, and supports real-time interactions among stakeholders.

### 1.3 Objective of the New System
The primary objective of PropKart is to:
- Create a unified portal for property buyers, sellers, and agents.
- Simplify listing, searching, and managing properties.
- Ensure data security, scalability, and performance.
- Provide intuitive dashboards and analytics for users.
- Integrate AI-powered property recommendations and chat assistance.

### 1.4 Problem Definition
The real estate market suffers from:
- Disconnected systems and poor data flow.
- Lack of transparency in property details and pricing.
- Manual processes that delay transactions.
- Limited access to verified agents and listings.

PropKart aims to solve these issues through automation, centralized data management, and a responsive interface.

### 1.5 Scope of the Project and Core Components
Scope:
PropKart serves as a full-stack web application for property management and transactions.

Core Components:
- 🏠 Property Listing Module
- 🔍 Search & Filter Engine
- 👤 User Authentication & Role Management
- 📊 Admin Dashboard
- 📩 Inquiry & Messaging System
- 🤖 AI Chat Assistant
- 📥 Property Import/Export System
- 📅 Visit Request Scheduler
- 🔔 Notification System
- 🛡 Security & Data Validation
- 🌐 SEO & Performance Optimization

### 1.6 Project Profile
- Project Name: PropKart
- Technology Stack: Django, HTML/CSS, JavaScript, SQLite
- Target Users: Property buyers, sellers, agents, and admins
- Deployment: Local development with potential cloud deployment

### 1.7 Assumptions and Constraints
Assumptions:
- Users have basic internet access and digital literacy.
- Property data is provided accurately by sellers/agents.

Constraints:
- Real-time updates depend on server performance.
- Legal compliance varies by region and must be handled externally.

### 1.8 Advantages and Limitations of the Proposed System
Advantages:
- Centralized property management
- Enhanced user experience with AI assistance
- Scalable and secure architecture
- Role-based access control
- Automated property import/export

Limitations:
- Requires internet connectivity
- Initial setup and data migration effort
- Limited offline functionality

### 1.9 Proposed Timeline Chart
| Phase                  | Duration     | Milestone                        |
|------------------------|--------------|----------------------------------|
| Requirement Analysis   | Week 1       | Finalize features and scope      |
| Design & Architecture  | Week 2–3     | UI/UX mockups, database schema   |
| Development            | Week 4–8     | Backend, frontend, integration   |
| Testing & QA           | Week 9–10    | Unit, integration, user testing  |
| Deployment             | Week 11      | Cloud setup and launch           |
| Documentation & Review | Week 12      | Final documentation and feedback |

## 📋 2. SYSTEM REQUIREMENTS

### 2.1 Requirement Determination
The requirements for PropKart were identified through:
- 📈 Market Analysis: Studying existing property platforms to understand gaps in usability, scalability, and security.
- 🗣 Stakeholder Interviews: Gathering input from potential users—buyers, sellers, and agents—on desired features and pain points.
- 🧪 Prototype Testing: Early mockups and feedback loops helped refine core functionalities and user flows.
- 🔍 Technical Feasibility: Evaluating Django's capabilities to support modular design, real-time data handling, and secure authentication.

These insights shaped PropKart into a solution that balances performance, user experience, and maintainability.

---

### 2.2 Targeted Users
PropKart is designed for a diverse set of users within the real estate ecosystem:

| 👤 User Type         | 🎯 Role & Needs                                                                 |
|----------------------|----------------------------------------------------------------------------------|
| Property Buyers  | Search listings, view property details, contact sellers/agents, schedule visits, use AI chat assistant                   |
| Property Sellers | List properties, manage inquiries, track views and feedback, import/export properties, manage visit requests                      |
| Agents/Brokers   | Manage multiple listings, communicate with clients, schedule property visits, access analytics     |
| Administrators   | Oversee platform activity, moderate content, generate analytics and reports      |

Each user type is supported through role-based access and tailored dashboards.

---

### 2.3 Requirement Specification

#### 🔧 Functional Requirements
- User Registration & Login with role-based access and OTP verification
- Property Listing Module with image/video uploads and bulk import
- Advanced Search & Filter by location, price, type, etc.
- Wishlist System for user engagement
- Real-time Chat Support (Client and Admin side)
- AI Chat Assistant with property recommendations
- Analytics Dashboard for property views and user activity
- Visit Request Scheduler for property visits
- Enquiry System for property inquiries
- Notification System for real-time updates
- Property Visibility Toggle for sellers
- Password Reset with OTP verification
- Seller Verification System

#### 🛡 Non-Functional Requirements
- Security: Encrypted data transmission, secure authentication, CSRF protection
- Scalability: Modular Django architecture to support future expansion
- Performance: Fast load times, optimized queries, caching
- Usability: Responsive design, intuitive navigation, accessibility compliance
- Maintainability: Clean codebase, reusable components, version control

## 🧠 3. SYSTEM DESIGN

### 3.1 Use Case Diagram
The use case diagram outlines the interactions between users and the system.

Actors:
- Buyer
- Seller
- Agent
- Admin

Key Use Cases:
- Register/Login with OTP verification
- List Property with bulk import
- Search Property with AI assistance
- View Property Details
- Schedule Visit Request
- Send Enquiry
- Chat Support with AI Assistant
- Track Views and Analytics
- Upload Property Media
- Manage Notifications
- Admin Analytics & Moderation

---

### 3.2 Class Diagram
Defines the structure of the system in terms of classes and relationships.

Core Classes:
- User (attributes: name, email, role, password, mobile, city, state, country, profile_picture, is_buyer, is_seller)
- Property (title, location, price, description, media, type, length, width, rooms, bedrooms, bathrooms, furnished, views, viewers, is_verified, is_hidden)
- PropertyImage (property, image, uploaded_at)
- Message (sender, receiver, timestamp, content, is_read)
- VisitRequest (property, buyer, preferred_date, preferred_time, status, visitor_details)
- Enquiry (property, buyer_name, buyer_email, buyer_phone, message, status)
- Notification (user, type, title, message, url, is_read, meta)
- ChatSession (user, session_id, created_at, updated_at, is_active)
- ChatMessage (session, message_type, content, referenced_properties)
- Wishlist (user, property, added_at)
- PasswordResetToken (user, token, created_at, expires_at, is_used)
- SellerRequest (user, token, created_at, expires_at)
- PropertyImportKey (seller, external_id, property, created_at)

---

### 3.3 Interaction Diagram
Illustrates how objects interact in a sequence.

Example: Property Search Flow
1. Buyer enters search query or uses AI chat.
2. System searches properties using PropertySearchService.
3. Results displayed with AI recommendations.
4. Buyer selects a property.
5. System fetches details and increments view count.

---

### 3.4 Activity Diagram
Represents workflows and decision points.

Example: Property Listing
- Seller logs in → selects "Add Property" → fills form → uploads media → submits → system validates → property listed.

Example: AI Chat Flow
- User opens chat → sends message → system searches properties → AI generates response → response displayed with property references.

---

### 3.5 Data Dictionary
Defines key data entities and their attributes.

| Entity        | Attribute           | Type        | Description                          |
|---------------|---------------------|-------------|--------------------------------------|
| User        | email             | String      | Unique user email                    |
| User        | is_buyer          | Boolean     | User can buy properties              |
| User        | is_seller         | Boolean     | User can sell properties             |
| Property    | price             | Decimal     | Property price                       |
| Property    | views             | Integer     | Number of property views             |
| Property    | viewers           | JSON        | List of viewer identifiers           |
| Property    | is_verified       | Boolean     | Property verification status         |
| Property    | is_hidden         | Boolean     | Property visibility to buyers        |
| Message     | is_read           | Boolean     | Message read status                  |
| VisitRequest| status            | String      | Visit request status                 |
| Notification| is_read           | Boolean     | Notification read status             |
| ChatMessage | referenced_properties | JSON    | Property IDs referenced in chat      |

---

### 3.6 User Interface Design (Using Expanded Use Cases)
Designs based on user goals and flows.

Screens:
- Login/Register with OTP verification
- Dashboard (role-specific)
- Property Listing Form with bulk import
- Search Results with AI recommendations
- Property Detail Page with enquiry and visit request
- AI Chat Interface
- Enquiry Management
- Visit Request Management
- Notification Center
- Admin Analytics Panel

---

### 3.7 Test Cases
Defines scenarios to validate system behavior.

| Test Case ID | Description                          | Input                  | Expected Output                     |
|--------------|--------------------------------------|------------------------|-------------------------------------|
| TC001        | Login with valid credentials         | Email, Password        | Redirect to dashboard               |
| TC002        | Search property by location          | "Surat"                | List of properties in Surat         |
| TC003        | AI chat property search              | "Show me 3BHK in Mumbai" | AI response with property recommendations |
| TC004        | Submit enquiry                       | Name, Email, Message   | Enquiry saved and notification sent |
| TC005        | Schedule visit request               | Date, Time, Property ID| Visit request created               |
| TC006        | Property bulk import                 | CSV file, Images ZIP   | Properties imported successfully    |
| TC007        | OTP verification                     | 6-digit OTP            | User verified and logged in         |
| TC008        | Password reset                       | Email, OTP, New Password| Password updated successfully       |
| TC009        | Toggle property visibility           | Property ID, Toggle    | Property visibility changed         |
| TC010        | Upload invalid file format           | .exe file              | Error: unsupported format           |

---

### 3.8 Report Design
Outlines how data is presented to users/admins.

Reports:
- Property View Analytics
- User Activity Logs
- Enquiry Summary
- Visit Request Status
- Chat History and AI Interactions
- Property Import/Export Logs

## 🛠 4. DEVELOPMENT

### 4.1 Appropriate Naming Conventions
To maintain clarity and consistency across the codebase:
- Models: Use singular nouns (e.g., Property, UserProfile, VisitRequest)
- Views: Use action-based names (e.g., create_property, view_dashboard, chat_ask)
- Templates: Use lowercase with underscores (e.g., property_detail.html, seller_dashboard.html)
- Static Files: Organize by type (css/, js/, images/) and use descriptive names
- Variables & Functions: Follow snake_case for Python and camelCase for JavaScript

> ✅ Consistent naming improves readability, debugging, and collaboration.

---

### 4.2 Use of Proper Comments
Comments are used to explain logic, mark TODOs, and clarify complex sections:
- Inline Comments: For brief clarifications (# Validate user input)
- Block Comments: For multi-step logic explanations
- Docstrings: For functions, classes, and modules using triple quotes (""" """)
- TODO/FIXME Tags: To highlight pending improvements or known issues

> 🧠 Comments are written in clear, concise English and avoid redundancy.

---

### 4.3 Proper Implementation of Business Logic
Business logic is centralized and modular:
- Models: Handle data relationships and constraints
- Views: Coordinate user requests and responses
- Services: Encapsulate reusable logic (e.g., PropertySearchService, ChatService)
- Forms: Manage input validation and clean data

> 🔄 Logic is tested for edge cases and optimized for performance.

---

### 4.4 Separation of Business Logic and Page View
Following Django's MVC (MTV) architecture:
- Models: Define data structure
- Templates: Handle presentation layer (HTML/CSS)
- Views: Act as controllers, linking models and templates
- Custom Tags/Filters: Used to keep templates clean and logic-free

> 🧩 This separation ensures maintainability and scalability.

---

### 4.5 Navigation (Flow of Control Across Pages)
Navigation is intuitive and role-based:
- Buyers: Home → Search/AI Chat → Property Detail → Enquiry/Visit Request
- Sellers: Dashboard → Add Property/Import → View Analytics → Manage Enquiries/Visits
- Agents: Dashboard → Manage Listings → Chat → Analytics
- Admins: Admin Panel → User Management → Reports → Moderation

> 🔗 URL routing is handled via urls.py, with named routes for clarity.

---

### 4.6 Server Side Validations (wherever required)
Critical validations are enforced on the backend:
- Authentication & Authorization: Role checks, session management
- Form Validation: Required fields, data types, constraints
- File Uploads: Size limits, format checks for images/videos
- Security Checks: CSRF protection, input sanitization
- OTP Validation: Time-based token validation
- Property Import: CSV structure validation, image format validation

> 🛡 Ensures data integrity and protects against malicious input.

---

### 4.7 Client Side Validations (wherever required)
Enhances user experience with real-time feedback:
- HTML5 Attributes: required, pattern, min, max
- JavaScript Validation: Custom checks before form submission
- Error Messages: Clear, contextual prompts for correction
- AJAX Checks: For dynamic validations (e.g., OTP verification, chat responses)

> ⚡ Reduces server load and improves responsiveness.

## 🚀 5. AGILE DOCUMENTATION

### 5.1 Agile Project Charter
Project Name: PropKart  
Vision Statement: To create a scalable, secure, and user-friendly property dealing platform that connects buyers, sellers, and agents through seamless digital interactions with AI-powered assistance.  
Business Objectives:
- Streamline property transactions
- Enhance user engagement through analytics and feedback
- Provide real-time communication and scheduling tools
- Integrate AI assistance for better property discovery
- Enable bulk property management for sellers

Stakeholders:
- Product Owner: [Your Name or Role]
- Scrum Master: [Assigned Role]
- Development Team: Frontend, Backend, QA
- End Users: Buyers, Sellers, Agents, Admins

---

### 5.2 Agile Roadmap / Schedule
| Quarter | Milestone                          | Key Deliverables                      |
|---------|------------------------------------|----------------------------------------|
| Q1      | MVP Development                    | Core modules: listing, search, login, OTP verification   |
| Q2      | Feature Expansion                  | Chat, AI assistant, feedback, analytics              |
| Q3      | Advanced Features                  | Property import/export, visit requests, notifications       |
| Q4      | Final Release & Marketing Launch   | Deployment, user onboarding, SEO       |

---

### 5.3 Agile Project Plan
Sprint Duration: 2 weeks  
Tools Used: GitHub, Trello/Jira, Slack, Django Test Framework  
Planning Activities:
- Sprint Planning
- Daily Standups
- Sprint Review & Retrospective  
Deliverables per Sprint: Working features, updated documentation, test coverage

---

### 5.4 Agile User Stories
Here are sample user stories written in the standard format:

- As a buyer, I want to search properties by location and price so that I can find relevant listings quickly.  
- As a buyer, I want to use AI chat assistance so that I can get personalized property recommendations.
- As a seller, I want to import multiple properties from CSV so that I can manage bulk listings efficiently.
- As a seller, I want to schedule and manage visit requests so that I can coordinate with potential buyers.
- As an agent, I want to track property views and enquiries so that I can analyze interest levels.
- As an admin, I want to view analytics dashboards so that I can monitor platform activity.

> 📌 Each story includes acceptance criteria and is linked to specific tasks in the sprint backlog.

---

### 5.5 Agile Release Plan
| Release Version | Features Included                          | Timeline     |
|------------------|---------------------------------------------|--------------|
| v1.0 (MVP)       | Login, Property Listing, Search, OTP Verification             | Week 4       |
| v1.1             | AI Chat, Feedback, Wishlist, Basic Analytics            | Week 8       |
| v1.2             | Property Import/Export, Visit Requests, Notifications              | Week 12      |
| v1.3 (Final)     | Advanced Analytics, UI Polish, SEO, Admin Reports               | Week 16      |

> ✅ Each release is tested and reviewed before deployment.

---

### 5.6 Agile Sprint Backlog
| Sprint | Tasks Included                                      | Assigned To     | Status     |
|--------|-----------------------------------------------------|------------------|------------|
| Sprint 1 | User Auth, Property Model, Basic Search, OTP Verification           | Backend Team     | ✅ Done     |
| Sprint 2 | AI Chat Integration, Property Import/Export              | Full Stack Team    | ✅ Done |
| Sprint 3 | Visit Requests, Enquiries, Notifications                 | Full Stack Devs  | ✅ Done  |
| Sprint 4 | Advanced Analytics, UI Polish, Testing                 | Frontend Team    | ✅ Done  |

---

### 5.7 Agile Test Plan
Testing Types:
- Unit Testing (models, views, services)
- Integration Testing (search, chat, import/export)
- UI Testing (forms, navigation, chat interface)
- Regression Testing (after each sprint)
- UAT (User Acceptance Testing) before release

Tools: Django Test Framework, Selenium, Postman (for API testing)

---

### 5.8 Earned Value & Burn Charts
Earned Value Management (EVM):
- Planned Value (PV): Estimated effort for completed tasks
- Earned Value (EV): Actual value delivered
- Actual Cost (AC): Time/resources spent

Burn Charts:
- Sprint Burndown Chart: Tracks remaining work per sprint
- Release Burnup Chart: Shows cumulative progress toward release goals

> 📊 These charts help monitor velocity, forecast delivery, and identify bottlenecks.

## 🧪 6. TESTING

### 6.1 Testing Method

PropKart employs a layered testing strategy to ensure reliability, performance, and usability across all modules. The following methods are used:

#### ✅ Unit Testing
- Focuses on individual components such as models, views, and utility functions.
- Ensures each function behaves as expected in isolation.
- Tools: unittest, pytest, Django's built-in test framework.

#### 🔗 Integration Testing
- Validates interactions between modules (e.g., property listing + search + AI chat).
- Ensures data flows correctly across components.

#### 🧭 Functional Testing
- Tests user-facing features like login, property scheduling, and chat.
- Verifies that each feature meets its functional requirements.

#### 🖥 UI/UX Testing
- Ensures forms, buttons, and navigation behave correctly across devices.
- Includes responsiveness and accessibility checks.

#### 🔐 Security Testing
- Validates authentication, authorization, and data protection.
- Includes CSRF, XSS, and input sanitization tests.

#### 🔁 Regression Testing
- Re-runs previous test cases after updates to ensure no new bugs are introduced.

#### 👥 User Acceptance Testing (UAT)
- Conducted with real users to validate usability and business logic before release.

---

### 6.2 Test Cases

Here's a sample set of test cases for key PropKart features:

| 🆔 Test Case ID | 🧪 Description                          | 📝 Input                          | ✅ Expected Output                          |
|----------------|------------------------------------------|----------------------------------|---------------------------------------------|
| TC001          | Login with valid credentials             | Email, Password                  | Redirect to user dashboard                  |
| TC002          | Login with invalid credentials           | Wrong Email/Password             | Show error message                          |
| TC003          | OTP verification for registration        | 6-digit OTP                      | User registered and logged in               |
| TC004          | Property listing submission              | Title, Location, Price, Media    | Property saved and visible in dashboard     |
| TC005          | Property bulk import                     | CSV file, Images ZIP             | Properties imported successfully            |
| TC006          | AI chat property search                  | "Show me 3BHK in Mumbai"         | AI response with property recommendations   |
| TC007          | Submit enquiry                           | Name, Email, Message             | Enquiry saved and notification sent         |
| TC008          | Schedule visit request                   | Date, Time, Property ID          | Visit request created and notification sent |
| TC009          | Toggle property visibility               | Property ID, Toggle              | Property visibility changed                 |
| TC010          | Password reset with OTP                  | Email, OTP, New Password         | Password updated successfully               |
| TC011          | Upload invalid file format               | .exe file                      | Error: unsupported format                   |
| TC012          | Admin analytics view                     | Admin login                      | Dashboard with charts and metrics           |
| TC013          | Unauthorized access to seller panel      | Buyer login                      | Access denied message                       |

> 📌 Each test case includes setup, execution steps, expected results, and post-conditions.

## 🔧 7. PROPOSED ENHANCEMENT

As PropKart evolves, several enhancements are proposed to improve functionality, scalability, and user experience. These enhancements are based on user feedback, market trends, and technical opportunities.

### 7.1 Feature Enhancements

- 📱 Mobile App Integration  
  Develop native Android and iOS apps to expand accessibility and support on-the-go property browsing and management.

- 🧠 Enhanced AI-Powered Property Recommendations  
  Improve machine learning algorithms to suggest properties based on user behavior, preferences, and location history with more sophisticated matching.

- 📍 Advanced Geo-Location Services  
  Enable map-based property search and real-time location tracking for scheduled visits with integration to Google Maps.

- 📅 Calendar Sync for Scheduling  
  Integrate with Google Calendar and Outlook to sync property visit schedules and reminders.

- 🔔 Real-Time Notifications  
  Push alerts for new listings, feedback responses, and chat messages using WebSockets or Firebase.

- 🧾 Document Upload & Verification  
  Allow sellers and agents to upload legal documents (e.g., ownership proof, floor plans) with optional admin verification.

- 📊 Advanced Analytics for Agents/Admins  
  Include heatmaps, conversion rates, and user engagement metrics in the dashboard.

- 💳 Payment Gateway Integration  
  Enable premium listings, agent subscriptions, and booking fees via Razorpay or Stripe.

---

### 7.2 Technical Enhancements

- ⚙ Microservices Architecture  
  Refactor core modules into microservices for better scalability and independent deployment.

- 🛡 OAuth & Social Login  
  Add Google, Facebook, and LinkedIn login options for faster onboarding.

- 📦 Docker & CI/CD Pipeline  
  Containerize the application and set up automated deployment pipelines using GitHub Actions or Jenkins.

- 🌐 Multilingual Support  
  Implement internationalization (i18n) to support multiple languages and expand user base.

- 🧪 Automated Testing Suite  
  Extend test coverage with Selenium, Pytest, and Postman for robust CI validation.

- 🔄 Database Migration to PostgreSQL  
  Migrate from SQLite to PostgreSQL for better performance and scalability in production.

---

### 7.3 Business & UX Enhancements

- 🎨 UI/UX Redesign  
  Conduct usability testing and redesign key flows for better accessibility and visual appeal.

- 👥 Community & Review System  
  Add user reviews for agents and properties to build trust and transparency.

- 📈 Advanced Search Filters  
  Implement more sophisticated search filters including price range sliders, map-based search, and saved searches.

- 🔍 Property Comparison Tool  
  Allow users to compare multiple properties side by side.

- 📊 Market Analytics Dashboard  
  Provide market trends, price analytics, and neighborhood insights.

## ✅ 8. CONCLUSION

PropKart represents a modern, scalable, and user-centric solution to the challenges of property dealing in the digital age. By integrating robust backend architecture with intuitive front-end design and AI-powered assistance, the platform bridges the gap between buyers, sellers, and agents—streamlining property transactions through automation, transparency, and real-time interaction.

Throughout this documentation, we've explored PropKart's system design, development methodology, Agile planning, and testing strategies. Each component—from the AI chat assistant to property import/export functionality, visit request scheduling, and comprehensive notification system—has been thoughtfully implemented to ensure a seamless user experience and operational efficiency.

The platform successfully integrates advanced features such as:
- AI-powered property recommendations and chat assistance
- Bulk property import/export capabilities
- Comprehensive visit request and enquiry management
- Real-time notifications and messaging
- OTP-based authentication and verification
- Advanced analytics and reporting

As the platform evolves, proposed enhancements such as mobile integration, payment gateway integration, and advanced analytics will further strengthen its value proposition. With a strong foundation in Django and a forward-thinking roadmap, PropKart is well-positioned to become a trusted hub in the real estate ecosystem.

This documentation serves not only as a technical guide but also as a blueprint for future innovation and collaboration.

## 🎓 9. PROJECT LEARNINGS

Developing PropKart has been a transformative experience, blending technical mastery with creative problem-solving. The journey offered valuable insights across multiple dimensions:

### 🔧 Technical Learnings
- Django Framework Mastery  
  Gained hands-on experience with Django's MTV architecture, ORM, and admin customization for scalable web development.

- AI Integration & Chat Services  
  Successfully integrated Google Gemini AI for property recommendations and chat assistance, learning about API integration and natural language processing.

- Advanced File Handling  
  Implemented bulk property import/export with CSV and ZIP file processing, including image validation and storage optimization.

- Real-time Features Implementation  
  Built notification systems, messaging, and visit request scheduling with proper state management and user experience considerations.

- Database Design & Optimization  
  Designed relational models for complex user interactions, property management, and chat systems with proper indexing and query optimization.

- Testing & Debugging  
  Practiced writing comprehensive unit and integration tests, and used Django's test framework to ensure reliability across modules.

---

### 🧠 Conceptual & Strategic Learnings
- Agile Development Workflow  
  Understood sprint planning, backlog grooming, and iterative delivery through Agile documentation and team coordination.

- User-Centric Design Thinking  
  Prioritized usability and accessibility by designing intuitive interfaces and responsive layouts with AI assistance.

- Security Awareness  
  Integrated authentication, role-based access, CSRF protection, and OTP verification to safeguard user data and platform integrity.

- Scalability Planning  
  Explored microservices, containerization, and CI/CD pipelines for future-proofing the application.

---

### 🌱 Personal Growth
- Problem-Solving Resilience  
  Overcame technical challenges like AI integration, bulk file processing, and complex user workflows with persistence and creativity.

- Collaboration & Communication  
  Improved teamwork and documentation skills by aligning with stakeholders and clearly articulating design decisions.

- Time Management & Prioritization  
  Balanced feature development with testing and documentation under tight deadlines.

- Confidence in Full-Stack Development  
  Built a complete, functional platform with advanced features—boosting confidence in both frontend and backend capabilities.

---

This project has laid a strong foundation for future endeavors in web development, AI integration, product design, and scalable architecture. PropKart is not just a platform—it's a testament to growth, innovation, and the power of learning by building.

## 📚 10. BIBLIOGRAPHY

The following resources were consulted during the development and documentation of PropKart:

### 📘 Technical Documentation & Frameworks
- Django Project Documentation – [https://docs.djangoproject.com](https://docs.djangoproject.com)
- Python Official Documentation – [https://docs.python.org](https://docs.python.org)
- Bootstrap Framework – [https://getbootstrap.com](https://getbootstrap.com)
- SQLite Documentation – [https://www.sqlite.org/docs.html](https://www.sqlite.org/docs.html)
- Google Gemini AI Documentation – [https://ai.google.dev/docs](https://ai.google.dev/docs)

### 🧠 Agile & Software Engineering References
- Agile Manifesto – [https://agilemanifesto.org](https://agilemanifesto.org)
- Scrum Guide – [https://scrumguides.org](https://scrumguides.org)
- IEEE Software Engineering Standards

### 🌐 Web Development & UI/UX
- MDN Web Docs (HTML, CSS, JavaScript) – [https://developer.mozilla.org](https://developer.mozilla.org)
- W3Schools Tutorials – [https://www.w3schools.com](https://www.w3schools.com)
- UX Design Principles – Nielsen Norman Group – [https://www.nngroup.com](https://www.nngroup.com)

### 📊 Tools & Platforms
- GitHub – Version Control and Collaboration
- Trello / Jira – Agile Project Management
- Lucidchart / Draw.io – Diagramming Tools
- Postman – API Testing
- Google Gemini AI – AI Chat Integration

### 🔧 Development Tools & Libraries
- Pillow (PIL) – Image Processing
- python-dotenv – Environment Variable Management
- Django Email Backend – SMTP Configuration
- CSV Module – File Processing

> 📌 Additional references may include academic papers, YouTube tutorials, or blog posts consulted during specific implementation phases.
