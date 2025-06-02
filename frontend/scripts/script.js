document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const fetchBtn = document.getElementById('fetch-btn');
    const videoUrlInput = document.getElementById('video-url');
    const videoInfoSection = document.getElementById('video-info');
    const loadingOverlay = document.getElementById('loading');
    const progressBar = loadingOverlay.querySelector('.progress-bar');
    const loadingText = loadingOverlay.querySelector('.loading-text');
    const notification = document.getElementById('notification');
    
    // Animation for elements with animate-pop-in class
    const animateElements = document.querySelectorAll('.animate-pop-in, .animate-slide-in');
    animateElements.forEach((element, index) => {
        element.style.animationDelay = `${index * 0.1}s`;
    });
    
    // Fetch video info when button is clicked
    fetchBtn.addEventListener('click', fetchVideoInfo);
    
    // Also fetch when Enter key is pressed in the input field
    videoUrlInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            fetchVideoInfo();
        }
    });
    
    function fetchVideoInfo() {
        const videoUrl = videoUrlInput.value.trim();
        
        // Validate URL
        if (!videoUrl) {
            showNotification('Please enter a YouTube URL', 'error');
            return;
        }
        
        if (!isValidYouTubeUrl(videoUrl)) {
            showNotification('Please enter a valid YouTube URL', 'error');
            return;
        }
        
        // Show loading overlay with progress
        loadingOverlay.classList.remove('hidden');
        progressBar.style.width = '0%';
        loadingText.textContent = 'Processing your request...';
        
        // For demo purposes, we'll simulate progress
        const progressInterval = setInterval(() => {
            const currentWidth = parseInt(progressBar.style.width) || 0;
            const newWidth = Math.min(currentWidth + 10, 90);
            progressBar.style.width = `${newWidth}%`;
            
            // Update loading text based on progress
            if (newWidth < 30) {
                loadingText.textContent = 'Connecting to YouTube...';
            } else if (newWidth < 60) {
                loadingText.textContent = 'Fetching video info...';
            } else if (newWidth < 90) {
                loadingText.textContent = 'Preparing download options...';
            }
        }, 300);
        
        // Simulate API call (in a real app, this would be a fetch to your backend)
        setTimeout(() => {
            clearInterval(progressInterval);
            progressBar.style.width = '100%';
            loadingText.textContent = 'Almost done...';
            
            setTimeout(() => {
                loadingOverlay.classList.add('hidden');
                
                // For demo purposes, we'll use mock data
                const mockVideoData = {
                    title: 'Amazing Nature Documentary - 4K Quality',
                    thumbnail: 'https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg',
                    duration: '12:34',
                    views: '1.2M views',
                    formats: [
                        { type: 'mp4', quality: '1080p', label: 'MP4 1080p' },
                        { type: 'mp4', quality: '720p', label: 'MP4 720p' },
                        { type: 'mp3', quality: '128kbps', label: 'MP3 Audio' },
                        { type: 'mp4', quality: '360p', label: 'MP4 360p' }
                    ]
                };
                
                displayVideoInfo(mockVideoData);
                
                // In a real app, you would make a fetch request to your backend:
                /*
                fetch('/api/video-info', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ url: videoUrl }),
                })
                .then(response => {
                    const reader = response.body.getReader();
                    const decoder = new TextDecoder();
                    let data = '';
                    
                    function pump() {
                        return reader.read().then(({ value, done }) => {
                            if (done) {
                                loadingOverlay.classList.add('hidden');
                                try {
                                    const finalData = JSON.parse(data);
                                    if (finalData.error) {
                                        showNotification(finalData.error, 'error');
                                    } else {
                                        displayVideoInfo(finalData);
                                    }
                                } catch (e) {
                                    showNotification('Failed to parse response', 'error');
                                }
                                return;
                            }
                            
                            data += decoder.decode(value);
                            try {
                                const progressData = JSON.parse(data);
                                if (progressData.progress) {
                                    progressBar.style.width = `${progressData.progress}%`;
                                    loadingText.textContent = progressData.message || 'Processing...';
                                }
                                data = ''; // Reset for next chunk
                            } catch (e) {
                                // Partial JSON, wait for more data
                            }
                            
                            return pump();
                        });
                    }
                    
                    return pump();
                })
                .catch(error => {
                    loadingOverlay.classList.add('hidden');
                    showNotification('Failed to fetch video info', 'error');
                    console.error('Error:', error);
                });
                */
            }, 500);
        }, 2000);
    }
    
    function isValidYouTubeUrl(url) {
        const pattern = /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.?be)\/.+$/;
        return pattern.test(url);
    }
    
    function displayVideoInfo(videoData) {
        // Update the DOM with video info
        
        document.getElementById('video-title').textContent = videoData.title;
        document.getElementById('thumbnail-img').src = videoData.thumbnail;
        document.getElementById('video-duration').textContent = videoData.duration;
        document.getElementById('video-views').textContent = videoData.views;
        
        // Create format buttons
        const formatButtonsContainer = document.getElementById('format-buttons');
        formatButtonsContainer.innerHTML = '';
        
        videoData.formats.forEach(format => {
            const button = document.createElement('button');
            button.className = 'format-btn';
            button.innerHTML = `<i class="fas fa-${format.type === 'mp3' ? 'music' : 'video'}"></i> ${format.label}`;
            
            button.addEventListener('click', () => {
                downloadVideo(format);
            });
            
            formatButtonsContainer.appendChild(button);
        });
        
        // Show the video info section with animation
        videoInfoSection.classList.remove('hidden');
        setTimeout(() => {
            videoInfoSection.classList.add('visible');
        }, 10);
    }
    
    function downloadVideo(format) {
        showNotification(`Preparing ${format.label} download...`, 'success');
        
        // Show loading overlay for download
        loadingOverlay.classList.remove('hidden');
        progressBar.style.width = '0%';
        loadingText.textContent = `Preparing ${format.label} download...`;
        
        // Simulate download progress
        const downloadInterval = setInterval(() => {
            const currentWidth = parseInt(progressBar.style.width) || 0;
            const newWidth = Math.min(currentWidth + 20, 100);
            progressBar.style.width = `${newWidth}%`;
            
            // Update loading text based on progress
            if (newWidth < 40) {
                loadingText.textContent = `Preparing ${format.label}...`;
            } else if (newWidth < 80) {
                loadingText.textContent = `Processing ${format.label}...`;
            } else {
                loadingText.textContent = `Finalizing ${format.label}...`;
            }
        }, 200);
        
        setTimeout(() => {
            clearInterval(downloadInterval);
            loadingOverlay.classList.add('hidden');
            showNotification(`Your ${format.label} download is ready!`, 'success');
            
            // In a real app, you might trigger the actual download here
            // window.location.href = `/download?url=${encodeURIComponent(videoUrlInput.value)}&format=${format.type}&quality=${format.quality}`;
        }, 1500);
    }
    
    function showNotification(message, type) {
        notification.textContent = message;
        notification.className = 'notification';
        
        if (type === 'error') {
            notification.style.backgroundColor = '#ff4d4d';
        } else {
            notification.style.backgroundColor = '#4CAF50';
        }
        
        notification.classList.add('show');
        
        setTimeout(() => {
            notification.classList.remove('show');
        }, 3000);
    }
    
    // Responsive menu toggle (for mobile)
    const navToggle = document.querySelector('.nav-toggle');
    if (navToggle) {
        navToggle.addEventListener('click', () => {
            document.querySelector('.header').classList.toggle('menu-open');
        });
    }
});