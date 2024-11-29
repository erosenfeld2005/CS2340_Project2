 document.addEventListener('DOMContentLoaded', function () {
    let slideIndex = 0; // curr index
    const slides = document.querySelectorAll('.slide');
    const dots = document.querySelectorAll('.dot');
    const animationDuration = 1500; // Duration in ms matching CSS animation
    const quizOptions = document.querySelectorAll('.quiz-options p');

    // Event listener for Start button
    const startButton = document.getElementById('start-button');
    if (startButton) {
        startButton.addEventListener('click', function() {
            // User has interacted with the page, audio can play
            showSlide(slideIndex, 'next'); // Start the slideshow
            this.style.display = 'none'; // Hide the start button
        });
    }

    /**
     * This function finds and displays the new slide
     * @param newIndex The new index of the slide we are displaying
     * @param direction Either 'next' or 'prev', depending on which arrow was clicked
     */
    function showSlide(newIndex, direction) {
        const outgoingSlide = slides[slideIndex];
        const incomingSlide = slides[newIndex];

        // Pause audio in outgoing slide and reset play/pause buttons
        const outgoingAudios = outgoingSlide.querySelectorAll('audio');
        outgoingAudios.forEach(audio => {
            audio.pause();
            audio.currentTime = 0; // Reset to start
            // Reset corresponding button text to 'Play'
            const button = outgoingSlide.querySelector(`.play-pause-button[data-audio-id="${audio.id}"]`);
            if (button) {
                button.textContent = 'Play';
            }
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

        // Update dot navigation
        dots.forEach(dot => dot.classList.remove('active'));
        dots[newIndex].classList.add('active');

        // Update slideIndex after the animation completes
        setTimeout(() => {
            slideIndex = newIndex; // Update slideIndex after the transition completes
        }, animationDuration);
    }

    /**
     * This function changes the slide given an amount to move
     * @param n The amount we want to move
     */
    function changeSlide(n) {
        const newSlideIndex = (slideIndex + n + slides.length) % slides.length;
        const direction = n > 0 ? 'next' : 'prev';
        showSlide(newSlideIndex, direction);
    }

    /**
     * This function displays the current slide
     * @param index The index of the current slide
     */
    function currentSlide(index) {
        const direction = index > slideIndex ? 'next' : 'prev';
        showSlide(index, direction);
    }

    // Initial display: Hide all slides except the first one
    slides.forEach((slide, index) => {
        if (index !== slideIndex) {
            slide.style.display = 'none';
        }
    });

    // Add event listeners to navigation arrows
    const prevButton = document.querySelector('.prev');
    const nextButton = document.querySelector('.next');

    if (prevButton) {
        prevButton.addEventListener('click', () => changeSlide(-1));
    }
    if (nextButton) {
        nextButton.addEventListener('click', () => changeSlide(1));
    }

    // Add event listeners to dots
    dots.forEach((dot, index) => {
        dot.addEventListener('click', () => currentSlide(index));
    });

    // Quiz functionality
    function handleQuizOptionClick(event) {
        const selectedOption = event.target;

        if (selectedOption.dataset.correct === 'true') {
            // Highlight the correct answer
            selectedOption.classList.add('selected');
            setTimeout(() => {
                // Transition to the next slide
                changeSlide(1); // Move to the next slide
            }, 500); // Wait for feedback before sliding
        } else {
            // Highlight incorrect answer
            selectedOption.classList.add('incorrect');
        }
    }

    // Add event listeners to quiz options
    quizOptions.forEach(option => {
        option.addEventListener('click', handleQuizOptionClick);
    });

    // Set up a MutationObserver to detect class changes in slides for Wrapped Summary logic
    const observer = new MutationObserver(() => updateLink());
    slides.forEach(slide => observer.observe(slide, { attributes: true, attributeFilter: ['class'] }));

    // Initial link setup for Wrapped Summary logic
    function updateLink() {
        const activeSlide = document.querySelector('.slide.active');
        const slideshowContainer = document.getElementById('slideshow-container');

        if (activeSlide && activeSlide.querySelector('h2').innerText === 'Wrapped Summary') {
            slideshowContainer.onclick = () => {
                window.location.href = "{% url 'spotify_login' %}";
            };
        } else {
            slideshowContainer.onclick = null; // Remove click event if not on "Wrapped Summary"
        }
    }

    // Initial link setup
    updateLink();
});

