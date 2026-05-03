// Property card hover animations
document.addEventListener('DOMContentLoaded', function() {
    // Animate property cards on hover
    const propertyCards = document.querySelectorAll('.property-item');
    propertyCards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.transform = 'translateY(-5px)';
            card.style.transition = 'transform 0.3s ease';
            card.style.boxShadow = '0 10px 20px rgba(0,0,0,0.1)';
        });
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'translateY(0)';
            card.style.boxShadow = 'none';
        });
    });

    // Dynamic property views counter
    function updatePropertyViews(propertyId) {
        const viewsElement = document.getElementById(`views-${propertyId}`);
        if (viewsElement) {
            fetch(`/api/property/${propertyId}/views/`)
                .then(response => response.json())
                .then(data => {
                    viewsElement.textContent = data.views;
                })
                .catch(error => console.error('Error updating views:', error));
        }
    }

    // Update views when property modal is opened
    const propertyLinks = document.querySelectorAll('[data-bs-toggle="modal"][data-bs-target="#propertyModal"]');
    propertyLinks.forEach(link => {
        link.addEventListener('click', () => {
            const propertyId = link.getAttribute('data-id');
            updatePropertyViews(propertyId);
        });
    });

    // Search autocomplete
    const searchInput = document.querySelector('input[name="q"]');
    if (searchInput) {
        let timeoutId;
        searchInput.addEventListener('input', (e) => {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => {
                const query = e.target.value;
                if (query.length >= 2) {
                    fetch(`/api/search/suggestions/?q=${encodeURIComponent(query)}`)
                        .then(response => response.json())
                        .then(data => {
                            // Create or update suggestions dropdown
                            let suggestionsDiv = document.getElementById('search-suggestions');
                            if (!suggestionsDiv) {
                                suggestionsDiv = document.createElement('div');
                                suggestionsDiv.id = 'search-suggestions';
                                suggestionsDiv.className = 'search-suggestions';
                                searchInput.parentNode.appendChild(suggestionsDiv);
                            }
                            suggestionsDiv.innerHTML = '';
                            data.suggestions.forEach(suggestion => {
                                const div = document.createElement('div');
                                div.className = 'suggestion-item';
                                div.textContent = suggestion;
                                div.addEventListener('click', () => {
                                    searchInput.value = suggestion;
                                    suggestionsDiv.innerHTML = '';
                                });
                                suggestionsDiv.appendChild(div);
                            });
                        })
                        .catch(error => console.error('Error fetching suggestions:', error));
                }
            }, 300);
        });

        // Close suggestions when clicking outside
        document.addEventListener('click', (e) => {
            if (!searchInput.contains(e.target)) {
                const suggestionsDiv = document.getElementById('search-suggestions');
                if (suggestionsDiv) {
                    suggestionsDiv.innerHTML = '';
                }
            }
        });
    }

    // Initialize AOS animations
    AOS.init({
        duration: 800,
        easing: 'ease',
        once: true
    });
});