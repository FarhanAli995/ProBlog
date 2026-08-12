/**
 * Gallery Tunnel Video Enhancement
 * Adds video autoplay on hover functionality for blog cards
 */

(function() {
  'use strict';

  class VideoHoverPlayer {
    constructor() {
      this.setupVideoHovers();
      this.observeNewCards();
    }

    setupVideoHovers() {
      // Find all blog cards
      document.querySelectorAll('.card-glass').forEach((card) => {
        if (!card.dataset.videoInitialized) {
          const videoUrl = card.getAttribute('data-video-url');
          const thumbnailImg = card.querySelector('img');

          if (videoUrl && videoUrl.trim() && thumbnailImg) {
            this.addVideoHoverToCard(card, videoUrl, thumbnailImg);
            card.dataset.videoInitialized = 'true';
          }
        }
      });
    }

    observeNewCards() {
      // Watch for dynamically added cards
      const observer = new MutationObserver(() => this.setupVideoHovers());
      observer.observe(document.body, { childList: true, subtree: true });
    }

      // Also check for video posts in gallery tunnel
      this.setupTunnelVideoThumbnails();
    }

    addVideoHoverToCard(card, videoUrl, thumbnailImg) {
      const imageContainer = thumbnailImg.parentElement;
      
      if (!imageContainer) return;
      
      // Ensure container has proper positioning
      if (imageContainer.style.position !== 'absolute') {
        imageContainer.style.position = 'relative';
      }
      
      // Create video element
      const video = document.createElement('video');
      video.preload = 'metadata';
      video.muted = true;
      video.loop = true;
      video.playsInline = true;
      video.style.cssText = `
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        object-fit: cover;
        opacity: 0;
        transition: opacity 0.3s ease;
        z-index: 2;
        display: block;
      `;
      
      // Set video source
      video.src = videoUrl;
      video.onloadedmetadata = () => {
        console.log('Video loaded:', videoUrl);
      };
      video.onerror = () => {
        console.warn('Failed to load video:', videoUrl);
      };

      // Add play button overlay
      const playButton = document.createElement('div');
      playButton.style.cssText = `
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 60px;
        height: 60px;
        background: rgba(0, 106, 204, 0.9);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        z-index: 3;
        opacity: 1;
        transition: opacity 0.3s ease, transform 0.3s ease;
        font-size: 28px;
        color: #FFFFFF;
        box-shadow: 0 4px 16px rgba(0, 106, 204, 0.4);
      `;
      playButton.innerHTML = '▶';
      playButton.addEventListener('mouseenter', () => {
        playButton.style.transform = 'translate(-50%, -50%) scale(1.1)';
      });
      playButton.addEventListener('mouseleave', () => {
        playButton.style.transform = 'translate(-50%, -50%) scale(1)';
      });

      // Add badge for video
      const videoBadge = document.createElement('span');
      videoBadge.style.cssText = `
        position: absolute;
        top: 10px;
        right: 10px;
        background: rgba(0, 106, 204, 0.95);
        border-radius: 6px;
        padding: 6px 12px;
        font-size: 11px;
        font-weight: 700;
        z-index: 4;
        color: #FFFFFF;
      `;
      videoBadge.textContent = '▶ VIDEO';

      imageContainer.appendChild(video);
      imageContainer.appendChild(playButton);
      imageContainer.appendChild(videoBadge);

      // Hover events for desktop
      card.addEventListener('mouseenter', () => {
        video.currentTime = 0;
        const playPromise = video.play();
        if (playPromise !== undefined) {
          playPromise
            .then(() => {
              video.style.opacity = '1';
              playButton.style.opacity = '0';
            })
            .catch((error) => {
              console.log('Autoplay prevented:', error);
              playButton.style.opacity = '1';
            });
        } else {
          video.style.opacity = '1';
          playButton.style.opacity = '0';
        }
      });

      card.addEventListener('mouseleave', () => {
        video.pause();
        video.currentTime = 0;
        video.style.opacity = '0';
        playButton.style.opacity = '1';
      });

      // Mobile tap to play
      playButton.addEventListener('click', (e) => {
        e.stopPropagation();
        if (video.paused) {
          video.play();
          video.style.opacity = '1';
          playButton.style.opacity = '0';
        } else {
          video.pause();
          video.style.opacity = '0';
          playButton.style.opacity = '1';
        }
      });
    }

    setupTunnelVideoThumbnails() {
      // Extract video thumbnails from blog posts for tunnel
      const videoThumbnails = [];
      
      document.querySelectorAll('[data-video-url]').forEach((elem) => {
        const videoUrl = elem.getAttribute('data-video-url');
        const thumbnail = elem.getAttribute('data-video-thumbnail');
        
        if (videoUrl && thumbnail) {
          videoThumbnails.push({
            url: videoUrl,
            thumbnail: thumbnail
          });
        }
      });

      // Store in window for tunnel to use
      window.problogVideoThumbnails = videoThumbnails;
    }

    // Static method to get video thumbnails for tunnel
    static getVideoThumbnails() {
      return window.problogVideoThumbnails || [];
    }
  }

  // Initialize on DOM ready
  document.addEventListener('DOMContentLoaded', () => {
    new VideoHoverPlayer();
  });

  // Export for external use
  window.VideoHoverPlayer = VideoHoverPlayer;
})();
