/**
 * LinguistFlow Dashboard Logic
 * Handles audio playback, speed control, and mastery updates.
 */

// Update Playback Speed for all audio elements
function updateSpeed(val) {
    const audios = document.querySelectorAll('audio');
    audios.forEach(a => a.playbackRate = val);
}

// Toggle Play/Pause for specific phrase audio
function togglePlay(id) {
    const audio = document.getElementById(id);
    if (audio.paused) {
        audio.play().catch(e => console.error("Playback failed:", e));
    } else {
        audio.pause();
    }
}

// Update Mastery Status in Database via AJAX
async function toggleMastery(id, isMastered) {
    try {
        const response = await fetch('/update-mastery', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/x-www-form-urlencoded' 
            },
            body: `phrase_id=${id}&is_mastered=${isMastered}`
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        // If successful, the UI stays updated as the checkbox is already toggled by user
    } catch (error) {
        console.error("Error updating mastery:", error);
        alert("Failed to update progress. Please check your connection.");
        
        // Revert the checkbox if the request failed
        const checkbox = document.querySelector(`.mastery-check[data-id="${id}"]`);
        if (checkbox) {
            checkbox.checked = !isMastered;
        }
    }
}

// Handle Language Filtering (Client Side for speed)
function updateLanguage(lang) {
    // Redirect to the index page with the new language filter
    window.location.href = "/index?language=" + (lang ? lang : "");
}
