let slideIndex = 0; // curr index
const slides = document.querySelectorAll('.slide');
const dots = document.querySelectorAll('.dot');
const animationDuration = 1500; // Duration in ms matching CSS animation


// Event listener Start button
document.getElementById('start-button').addEventListener('click', function() {
    // User has interacted with the page, audio can play
    showSlide(slideIndex, 'next'); // Start the slideshow
    this.style.display = 'none'; // Hide the start button
});

/**
 * This function finds and displays in the new slide
 * @param newIndex The new index of the slide we are displaying
 * @param direction Either next or before, depending on which arrow was flicked
 */
function showSlide(newIndex, direction) {
    const outgoingSlide = slides[slideIndex];
    const incomingSlide = slides[newIndex];

    // Pause audio in outgoing slide
    const outgoingAudios = outgoingSlide.querySelectorAll('audio');
    outgoingAudios.forEach(audio => {
        audio.pause();
        audio.currentTime = 0; // Reset to start
    });

    // Reset all slides to remove animations and hide them initially
    slides.forEach(slide => {
        slide.classList.remove('active', 'outgoing-left', 'incoming-right', 'outgoing-right', 'incoming-left');
        slide.style.display = 'none';
    });

    // Ensure the outgoing slide is visible before animating out
    outgoingSlide.style.display = 'block';
    outgoingSlide.style.zIndex = 2; // Set outgoing slide behind incoming

    // Apply the correct animation classes based on direction
    if (direction === 'next') {
        outgoingSlide.classList.add('outgoing-left');
        incomingSlide.classList.add('incoming-right');
    } else {
        outgoingSlide.classList.add('outgoing-right');
        incomingSlide.classList.add('incoming-left');
    }

    // Ensure the incoming slide is above the outgoing slide and visible
    incomingSlide.style.display = 'block';
    incomingSlide.style.zIndex = 1;
    incomingSlide.classList.add('active');

    // Play audio in incoming slide
    const incomingAudios = incomingSlide.querySelectorAll('audio');
    incomingAudios.forEach(audio => {
        // Attempt to play the audio
        audio.play().catch(error => {
            // Handle any playback errors
            console.error('Error playing audio:', error);
        });
    });

    // Update dot navigation
    dots.forEach(dot => dot.classList.remove('active'));
    dots[newIndex].classList.add('active');

    // Hide the outgoing slide after the animation completes
    setTimeout(() => {
        // outgoingSlide.style.display = 'none'; // Hide the outgoing slide
        slideIndex = newIndex; // Update slideIndex after the transition completes
    }, animationDuration);
}

/**
 * This function changes the slide given an amount to move
 * @param n The amove we want to move
 */
function changeSlide(n) {
    const newSlideIndex = (slideIndex + n + slides.length) % slides.length;
    const direction = n > 0 ? 'next' : 'prev';
    showSlide(newSlideIndex, direction);
}

/**
 * This function displays the current slide
 * @param index
 */
function currentSlide(index) {
    const direction = index > slideIndex ? 'next' : 'prev';
    showSlide(index, direction);
}

// Initial display
showSlide(slideIndex, 'next');

document.addEventListener('DOMContentLoaded', function () {
    const slideshowContainer = document.getElementById('slideshow-container');

    /**
     * This function updates the link to not work if not on wrapped summary
     */
    function updateLink() {
        const activeSlide = document.querySelector('.slide.active');
        if (activeSlide && activeSlide.querySelector('h2').innerText === 'Wrapped Summary') {
            slideshowContainer.onclick = () => {
                window.location.href = "{% url 'spotify_login' %}";
            };
        } else {
            slideshowContainer.onclick = null; // Remove click event if not on "Wrapped Summary"
        }
    }

    // Set up a MutationObserver to detect class changes in slides
    const observer = new MutationObserver(updateLink);
    slides.forEach(slide => observer.observe(slide, { attributes: true, attributeFilter: ['class'] }));

    // Initial link setup
    updateLink();
});
