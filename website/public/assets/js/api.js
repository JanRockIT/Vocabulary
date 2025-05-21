// API Configuration
const API_BASE_URL = 'https://vocabulary-g8t6.onrender.com';

// CORS-Proxy für lokale Entwicklung (falls nötig)
const USE_CORS_PROXY = false;
const CORS_PROXY = 'https://cors-anywhere.herokuapp.com/';

// Funktion zum Generieren der URL mit optionalem CORS-Proxy
function getApiUrl(endpoint) {
    return USE_CORS_PROXY ? CORS_PROXY + API_BASE_URL + endpoint : API_BASE_URL + endpoint;
}

// Toast notification function
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    let icon = '';
    if (type === 'success') icon = '<i class="fas fa-check-circle"></i>';
    else if (type === 'error') icon = '<i class="fas fa-exclamation-circle"></i>';
    else icon = '<i class="fas fa-info-circle"></i>';
    
    toast.innerHTML = `${icon} ${message}`;
    toastContainer.appendChild(toast);
    
    // Remove toast after 3 seconds
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

// Modal functions
function openModal(modalId) {
    document.getElementById(modalId).style.display = 'flex';
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

// API Functions
async function getCollections() {
    try {
        // Backend-Endpunkt /collections verwenden
        const response = await fetch(`${API_BASE_URL}/collections`);
        if (!response.ok) {
            throw new Error('Failed to fetch collections');
        }
        const data = await response.json();
        
        // Convert array response to array of objects and filter out collections with status 99
        if (Array.isArray(data)) {
            return data
                .filter(collectionArray => collectionArray[5] !== 99) // Filter out status 99
                .map(collectionArray => ({
                    id: collectionArray[7],
                    name: collectionArray[0],
                    source_language: collectionArray[1],
                    target_language: collectionArray[2],
                    learned_words: collectionArray[3],
                    progress_percent: parseFloat(collectionArray[4]) || 0,
                    status: collectionArray[5] || 0,
                    total_words: collectionArray[6],
                    created_at: collectionArray[8] || new Date().toISOString()
                }));
        }
        
        console.warn('Unexpected collections response format:', data);
        return [];
    } catch (error) {
        console.error('Error fetching collections:', error);
        showToast('Failed to load collections. Please try again.', 'error');
        return [];
    }
}

async function getCollection(collectionId) {
    try {
        const response = await fetch(`${API_BASE_URL}/collection?collection_id=${collectionId}`);
        if (!response.ok) {
            throw new Error('Failed to fetch collection');
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching collection:', error);
        showToast('Failed to load collection details. Please try again.', 'error');
        return null;
    }
}

async function getPairs(collectionId) {
    try {
        const response = await fetch(`${API_BASE_URL}/collection/${collectionId}/pairs`);
        if (!response.ok) {
            throw new Error('Failed to fetch pairs');
        }
        const data = await response.json();
        
        // Convert array response to array of objects
        if (Array.isArray(data)) {
            return data.map(pairArray => ({
                id: pairArray[0],
                source_word: pairArray[1],
                target_word: pairArray[2],
                interval: pairArray[3] || 0,
                next_review: pairArray[4],
                created_at: pairArray[5],
                updated_at: pairArray[6],
                collection_id: pairArray[7]
            }));
        }
        
        console.warn('Unexpected pairs response format:', data);
        return [];
    } catch (error) {
        console.error('Error fetching pairs:', error);
        showToast('Failed to load word pairs. Please try again.', 'error');
        return [];
    }
}

async function getNextPair(collectionId) {
    try {
        const response = await fetch(`${API_BASE_URL}/pair/next?collection_id=${collectionId}`);
        if (!response.ok) {
            throw new Error('Failed to fetch next pair');
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching next pair:', error);
        showToast('Failed to get next pair. Please try again.', 'error');
        return null;
    }
}

async function createCollection(name, sourceLanguage, targetLanguage) {
    try {
        const response = await fetch(`${API_BASE_URL}/collection`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                collection_name: name,
                source_language: sourceLanguage,
                target_language: targetLanguage
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to create collection');
        }
        
        const result = await response.json();
        showToast('Collection created successfully!', 'success');
        return result.collection_id;
    } catch (error) {
        console.error('Error creating collection:', error);
        showToast('Failed to create collection. Please try again.', 'error');
        return null;
    }
}

async function updateCollection(collectionId, fields) {
    try {
        const columns = Object.keys(fields);
        const values = Object.values(fields);
        
        const response = await fetch(`${API_BASE_URL}/collection/change`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                collection_id: collectionId,
                columns: columns,
                values: values
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to update collection');
        }
        
        showToast('Collection updated successfully!', 'success');
        return true;
    } catch (error) {
        console.error('Error updating collection:', error);
        showToast('Failed to update collection. Please try again.', 'error');
        return false;
    }
}

async function deleteCollection(collectionId) {
    try {
        const response = await fetch(`${API_BASE_URL}/collection/delete`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                collection_id: collectionId
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to delete collection');
        }
        
        showToast('Collection deleted successfully!', 'success');
        return true;
    } catch (error) {
        console.error('Error deleting collection:', error);
        showToast('Failed to delete collection. Please try again.', 'error');
        return false;
    }
}

async function addPair(collectionId, sourceWord, targetWord) {
    try {
        const response = await fetch(`${API_BASE_URL}/pair`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                collection_id: collectionId,
                source_word: sourceWord,
                target_word: targetWord
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to add word pair');
        }
        
        showToast('Word pair added successfully!', 'success');
        return true;
    } catch (error) {
        console.error('Error adding word pair:', error);
        showToast('Failed to add word pair. Please try again.', 'error');
        return false;
    }
}

async function updatePair(collectionId, pairId, sourceWord, targetWord) {
    try {
        const response = await fetch(`${API_BASE_URL}/pair/change`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                collection_id: collectionId,
                pair_id: pairId,
                columns: ['source_word', 'target_word'],
                values: [sourceWord, targetWord]
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to update word pair');
        }
        
        showToast('Word pair updated successfully!', 'success');
        return true;
    } catch (error) {
        console.error('Error updating word pair:', error);
        showToast('Failed to update word pair. Please try again.', 'error');
        return false;
    }
}

async function deletePair(collectionId, pairId) {
    try {
        const response = await fetch(`${API_BASE_URL}/pair/delete`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                collection_id: collectionId,
                pair_id: pairId
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to delete word pair');
        }
        
        showToast('Word pair deleted successfully!', 'success');
        return true;
    } catch (error) {
        console.error('Error deleting word pair:', error);
        showToast('Failed to delete word pair. Please try again.', 'error');
        return false;
    }
}

async function updatePairStatus(collectionId, pairId, known) {
    try {
        const response = await fetch(`${API_BASE_URL}/pair/update`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                collection_id: collectionId,
                pair_id: pairId,
                known: known
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to update learning status');
        }
        
        return true;
    } catch (error) {
        console.error('Error updating learning status:', error);
        showToast('Failed to update learning status. Please try again.', 'error');
        return false;
    }
}

async function startLearningCollection(collectionId) {
    try {
        const response = await fetch(`${API_BASE_URL}/collection/learn`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                collection_id: collectionId
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to start learning mode');
        }
        
        return true;
    } catch (error) {
        console.error('Error starting learning mode:', error);
        showToast('Failed to start learning mode. Please try again.', 'error');
        return false;
    }
}

async function addLearningHistory(collectionId, pairId) {
    try {
        const response = await fetch(`${API_BASE_URL}/history`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                collection_id: collectionId,
                pair_id: pairId
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to record history');
        }
        
        return true;
    } catch (error) {
        console.error('Error recording history:', error);
        return false;
    }
}

// Helper function to format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Helper function to create a collection card
function createCollectionCard(collection) {
    // Format of collection: [name, sourceLang, targetLang, totalLearned, progressPercent, learnedRatio, totalWords, collectionId, date]
    const [name, sourceLang, targetLang, totalLearned, progressPercent, , totalWords, collectionId, date] = collection;
    
    const card = document.createElement('div');
    card.className = 'collection-card';
    card.dataset.id = collectionId;
    
    // Calculate progress percentage
    const progress = parseFloat(progressPercent);
    
    card.innerHTML = `
        <h3 class="collection-title">${name}</h3>
        <div class="collection-details">
            <div class="collection-languages">
                <span>${sourceLang}</span> → <span>${targetLang}</span>
            </div>
            <div class="collection-progress">${progress}% complete</div>
        </div>
        <div class="collection-stats">
            <div class="stat stat-learned">
                <i class="fas fa-check-circle"></i>
                <span>${totalLearned} learned</span>
            </div>
            <div class="stat stat-total">
                <i class="fas fa-book"></i>
                <span>${totalWords} total</span>
            </div>
        </div>
        <div class="collection-footer">
            <div class="collection-date">${formatDate(date)}</div>
            <div class="collection-actions">
                <i class="fas fa-edit action-icon edit-collection-btn" title="Edit Collection"></i>
                <i class="fas fa-trash action-icon delete-collection-btn" title="Delete Collection"></i>
            </div>
        </div>
    `;
    
    return card;
}
