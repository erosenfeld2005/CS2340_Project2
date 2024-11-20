document.addEventListener('DOMContentLoaded', function () {
    let slideIndex = 0; // curr index
    const slides = document.querySelectorAll('.slide');
    const dots = document.querySelectorAll('.dot');
    const animationDuration = 1500; // Duration in ms matching CSS animation

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
     * @param index
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

    // Add event listeners to play/pause buttons
    const playPauseButtons = document.querySelectorAll('.play-pause-button');
    playPauseButtons.forEach(button => {
        button.addEventListener('click', function() {
            const audioId = this.getAttribute('data-audio-id');
            const audioElement = document.getElementById(audioId);

            // Pause any other playing audio
            const allAudios = document.querySelectorAll('audio');
            allAudios.forEach(audio => {
                if (audio !== audioElement) {
                    audio.pause();
                    audio.currentTime = 0;
                    // Reset other play/pause buttons
                    const otherButton = document.querySelector(`.play-pause-button[data-audio-id="${audio.id}"]`);
                    if (otherButton) {
                        otherButton.textContent = 'Play';
                    }
                }
            });

            // Play or pause the audio
            if (audioElement.paused) {
                audioElement.play();
                this.textContent = 'Pause';
            } else {
                audioElement.pause();
                this.textContent = 'Play';
            }
        });
    });

    document.getElementById('instagram-share-btn').addEventListener('click', function () {
    captureSlideAndShare('instagram');
    });

    document.getElementById('twitter-share-btn').addEventListener('click', function () {
        captureSlideAndShare('twitter');
    });

    document.getElementById('linkedin-share-btn').addEventListener('click', function () {
        captureSlideAndShare('linkedin');
    });

    function captureSlideAndShare(platform) {
        const slide8 = document.querySelector('#slide-8'); // Select Slide 8
        const saveButton = slide8.querySelector('.save-button'); // Select the Save Button

        // Temporarily hide the Save Button
        saveButton.style.display = 'none';

        // Use html2canvas to capture the slide
        html2canvas(slide8).then(canvas => {
            const image = canvas.toDataURL('image/png');

            // Restore the Save Button
            saveButton.style.display = 'block';

            // Share the image based on the platform
            if (platform === 'instagram') {
                // Instagram-specific logic (manual upload since API limitations exist)
                downloadImage(image, 'wrapped-summary.png');
            } else if (platform === 'twitter') {
                const twitterUrl = `https://twitter.com/intent/tweet?text=Check%20out%20my%20Wrapped%20Summary!&url=${image}`;
                window.open(twitterUrl, '_blank');
            } else if (platform === 'linkedin') {
                const linkedinUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${image}`;
                window.open(linkedinUrl, '_blank');
            }
        });
    }

    function downloadImage(dataUrl, filename) {
        const link = document.createElement('a');
        link.href = dataUrl;
        link.download = filename;
        link.click();
    }

});
