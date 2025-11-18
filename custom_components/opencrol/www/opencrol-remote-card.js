// OpenCtrol Remote Card for Home Assistant Lovelace
// Version: 3.0.0
// Complete redesign with big touchpad

(function() {
  'use strict';

  // Load CSS (only once, check if already loaded)
  const cssHref = '/local/opencrol/opencrol-remote-card.css';
  if (!document.querySelector(`link[href="${cssHref}"]`)) {
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.type = 'text/css';
    link.href = cssHref;
    document.head.appendChild(link);
  }

class OpenCtrolRemoteCard extends HTMLElement {
  constructor() {
    super();
    this._screenStreamUrl = null;
    this._imgElement = null;
    this._fullscreenOverlay = null;
    this._activeModifiers = new Set();
    this._isFullscreenOpen = false;
  }

  static getStubConfig() {
    return {
      type: 'custom:opencrol-remote-card',
      entity: '',
      base_url: null
    };
  }

  setConfig(config) {
    if (!config.entity) {
      throw new Error('Entity is required');
    }
    this.config = config;
    this.entity = config.entity;
  }

  set hass(hass) {
    this._hass = hass;
    if (!this._hass || !this.config) return;
    this.updateCard();
  }

  connectedCallback() {
    this.updateCard();
    // Close fullscreen on ESC key (only add once)
    if (!this._escKeyHandler) {
      this._escKeyHandler = this._handleEscKey.bind(this);
      document.addEventListener('keydown', this._escKeyHandler);
    }
  }

  disconnectedCallback() {
    // Stop screen stream when card is removed
    if (this._imgElement) {
      this._imgElement.src = '';
      this._imgElement = null;
    }
    this.closeFullscreenRemote();
    // Remove event listeners
    if (this._escKeyHandler) {
      document.removeEventListener('keydown', this._escKeyHandler);
      this._escKeyHandler = null;
    }
    if (this._outsideClickHandler) {
      document.removeEventListener('click', this._outsideClickHandler);
      this._outsideClickHandler = null;
    }
  }

  _handleEscKey(e) {
    if (e.key === 'Escape' && this._isFullscreenOpen) {
      this.closeFullscreenRemote();
    }
  }

  updateCard() {
    if (!this.config || !this._hass) return;

    const entity = this._hass.states[this.config.entity];
    if (!entity) {
      this.innerHTML = '<ha-card><div class="error">Entity not found</div></ha-card>';
      return;
    }

    const attributes = entity.attributes || {};
    
    // Get status from coordinator data via attributes (not entity state)
    // The coordinator exposes status in attributes.status
    const status = attributes.status || 'offline';
    const isOnline = status === 'online';
    
    // Get all monitor-related data first
    const monitors = attributes.monitors || [];
    const currentMonitor = attributes.current_monitor !== undefined ? attributes.current_monitor : 0;
    
    // Get base URL from entity attributes or config
    const baseUrl = this.config.base_url || this.getBaseUrlFromEntity(entity);
    // Always include monitor parameter (0 is default)
    const monitorParam = `?monitor=${currentMonitor}`;
    this._screenStreamUrl = baseUrl ? `${baseUrl}/api/v1/screenstream/stream${monitorParam}` : null;

    const clientId = attributes.client_id || entity.attributes?.friendly_name || this.config.entity;
    const masterVolume = attributes.master_volume !== undefined ? Math.round(attributes.master_volume * 100) : 0;
    const audioApps = attributes.audio_apps || [];
    const audioDevices = attributes.audio_devices || [];
    const defaultDeviceId = attributes.default_output_device || (audioDevices.length > 0 ? audioDevices[0].id : '');
    const isScreenCaptureActive = attributes.screen_capture_active !== undefined ? attributes.screen_capture_active : false;
    const shouldShowStream = isOnline && this._screenStreamUrl && isScreenCaptureActive;

    // New compact title bar with icons only
    this.innerHTML = `
      <ha-card>
        <div class="card-header-compact">
          <div class="header-left-compact">
            <div class="status-icon ${isOnline ? 'online' : 'offline'}" title="${isOnline ? 'Online' : 'Offline'}">
              <ha-icon icon="${isOnline ? 'mdi:circle' : 'mdi:circle-outline'}"></ha-icon>
            </div>
            <div class="client-name">${this._escapeHtml(clientId)}</div>
          </div>
          <div class="header-icons-compact">
            ${isOnline ? `
              <button class="icon-btn ${isScreenCaptureActive ? 'active' : ''}" id="power-on-btn" title="Turn On Screen">
                <ha-icon icon="mdi:power"></ha-icon>
              </button>
              <button class="icon-btn ${!isScreenCaptureActive ? 'active' : ''}" id="power-off-btn" title="Turn Off Screen">
                <ha-icon icon="mdi:power-off"></ha-icon>
              </button>
            ` : ''}
            <div class="monitor-icons" title="Monitor Selection">
              ${monitors.length > 0 ? monitors.map((monitor, index) => `
                <button class="icon-btn monitor-icon ${index === currentMonitor ? 'active' : ''}" 
                        data-monitor-index="${index}" 
                        title="Monitor ${index + 1}">
                  ${index + 1}
                </button>
              `).join('') : ''}
            </div>
            <button class="icon-btn" id="sound-btn" title="Sound Mixer">
              <ha-icon icon="mdi:volume-high"></ha-icon>
            </button>
            <button class="icon-btn" id="keyboard-btn" title="Keyboard">
              <ha-icon icon="mdi:keyboard"></ha-icon>
            </button>
            <button class="icon-btn" id="lock-btn" title="Lock Workstation">
              <ha-icon icon="mdi:lock"></ha-icon>
            </button>
          </div>
        </div>
        
        <div class="card-content">
          <!-- Big Touchpad Area -->
          <div class="touchpad-container ${!isOnline ? 'offline' : ''}" id="touchpad-container">
            ${shouldShowStream ? `
              <div class="screen-wrapper">
                <img id="screen-stream" 
                     src="${this._screenStreamUrl}" 
                     alt="Screen Stream"
                     class="screen-stream"
                     loading="eager"
                     style="display: none;">
                <div id="screen-overlay" class="screen-overlay" style="display: none;"></div>
                <button class="fullscreen-btn" title="Fullscreen" aria-label="Open Fullscreen" style="display: none;">
                  <ha-icon icon="mdi:fullscreen"></ha-icon>
                </button>
              </div>
            ` : ''}
            <div class="touchpad-area ${shouldShowStream && isScreenCaptureActive ? 'hidden' : ''}" id="touchpad-area">
              <div class="touchpad-visual">
                <div class="touchpad-icon">${isOnline ? '🖱️' : '📴'}</div>
                <div class="touchpad-text">${isOnline ? 'Touchpad' : 'Device Offline'}</div>
                <div class="touchpad-hint">${isOnline ? 'Drag to move mouse • Tap to click • Scroll with two fingers' : 'Waiting for connection...'}</div>
              </div>
            </div>
          </div>

          <!-- Keyboard Popup Menu -->
          <div class="popup-menu keyboard-menu" id="keyboard-menu">
            <div class="popup-header">
              <div class="popup-title">Keyboard</div>
              <button class="popup-close" aria-label="Close">
                <ha-icon icon="mdi:close"></ha-icon>
              </button>
            </div>
            <div class="popup-content">
              <div class="input-group">
                <input type="text" id="text-input" placeholder="Type text here..." class="text-input" aria-label="Text Input">
                <button class="control-btn" id="type-btn" aria-label="Send Text">
                  <ha-icon icon="mdi:send"></ha-icon> Send
                </button>
              </div>
              
              <!-- Function Keys Row -->
              <div class="keyboard-row">
                <button class="keyboard-key" data-key="ESC">Esc</button>
                <button class="keyboard-key" data-key="F1">F1</button>
                <button class="keyboard-key" data-key="F2">F2</button>
                <button class="keyboard-key" data-key="F3">F3</button>
                <button class="keyboard-key" data-key="F4">F4</button>
                <button class="keyboard-key" data-key="F5">F5</button>
                <button class="keyboard-key" data-key="F6">F6</button>
                <button class="keyboard-key" data-key="F7">F7</button>
                <button class="keyboard-key" data-key="F8">F8</button>
                <button class="keyboard-key" data-key="F9">F9</button>
                <button class="keyboard-key" data-key="F10">F10</button>
                <button class="keyboard-key" data-key="F11">F11</button>
                <button class="keyboard-key" data-key="F12">F12</button>
              </div>

              <!-- Modifier Keys Row -->
              <div class="keyboard-row">
                <button class="keyboard-key toggle" data-key="CTRL">Ctrl</button>
                <button class="keyboard-key toggle" data-key="ALT">Alt</button>
                <button class="keyboard-key toggle" data-key="SHIFT">Shift</button>
                <button class="keyboard-key toggle" data-key="WIN">Win</button>
                <div class="keyboard-spacer"></div>
                <button class="keyboard-key" data-key="TAB">Tab</button>
                <button class="keyboard-key" data-key="ENTER">Enter</button>
                <button class="keyboard-key" data-key="BACKSPACE">⌫</button>
                <button class="keyboard-key" data-key="DELETE">Del</button>
              </div>

              <!-- Main Keys Row -->
              <div class="keyboard-row">
                <button class="keyboard-key" data-key="1">1</button>
                <button class="keyboard-key" data-key="2">2</button>
                <button class="keyboard-key" data-key="3">3</button>
                <button class="keyboard-key" data-key="4">4</button>
                <button class="keyboard-key" data-key="5">5</button>
                <button class="keyboard-key" data-key="6">6</button>
                <button class="keyboard-key" data-key="7">7</button>
                <button class="keyboard-key" data-key="8">8</button>
                <button class="keyboard-key" data-key="9">9</button>
                <button class="keyboard-key" data-key="0">0</button>
              </div>

              <!-- Letter Keys Row 1 -->
              <div class="keyboard-row">
                <button class="keyboard-key" data-key="Q">Q</button>
                <button class="keyboard-key" data-key="W">W</button>
                <button class="keyboard-key" data-key="E">E</button>
                <button class="keyboard-key" data-key="R">R</button>
                <button class="keyboard-key" data-key="T">T</button>
                <button class="keyboard-key" data-key="Y">Y</button>
                <button class="keyboard-key" data-key="U">U</button>
                <button class="keyboard-key" data-key="I">I</button>
                <button class="keyboard-key" data-key="O">O</button>
                <button class="keyboard-key" data-key="P">P</button>
              </div>

              <!-- Letter Keys Row 2 -->
              <div class="keyboard-row">
                <button class="keyboard-key" data-key="A">A</button>
                <button class="keyboard-key" data-key="S">S</button>
                <button class="keyboard-key" data-key="D">D</button>
                <button class="keyboard-key" data-key="F">F</button>
                <button class="keyboard-key" data-key="G">G</button>
                <button class="keyboard-key" data-key="H">H</button>
                <button class="keyboard-key" data-key="J">J</button>
                <button class="keyboard-key" data-key="K">K</button>
                <button class="keyboard-key" data-key="L">L</button>
              </div>

              <!-- Letter Keys Row 3 -->
              <div class="keyboard-row">
                <button class="keyboard-key" data-key="Z">Z</button>
                <button class="keyboard-key" data-key="X">X</button>
                <button class="keyboard-key" data-key="C">C</button>
                <button class="keyboard-key" data-key="V">V</button>
                <button class="keyboard-key" data-key="B">B</button>
                <button class="keyboard-key" data-key="N">N</button>
                <button class="keyboard-key" data-key="M">M</button>
              </div>

              <!-- Arrow Keys Row -->
              <div class="keyboard-row">
                <button class="keyboard-key" data-key="UP">↑</button>
                <button class="keyboard-key" data-key="LEFT">←</button>
                <button class="keyboard-key" data-key="DOWN">↓</button>
                <button class="keyboard-key" data-key="RIGHT">→</button>
                <div class="keyboard-spacer"></div>
                <button class="keyboard-key" data-key="HOME">Home</button>
                <button class="keyboard-key" data-key="END">End</button>
                <button class="keyboard-key" data-key="PAGEUP">PgUp</button>
                <button class="keyboard-key" data-key="PAGEDOWN">PgDn</button>
              </div>

              <!-- Shortcuts Row -->
              <div class="keyboard-row shortcuts-row">
                <button class="keyboard-key shortcut" data-keys="CTRL+C">Ctrl+C</button>
                <button class="keyboard-key shortcut" data-keys="CTRL+V">Ctrl+V</button>
                <button class="keyboard-key shortcut" data-keys="CTRL+X">Ctrl+X</button>
                <button class="keyboard-key shortcut" data-keys="CTRL+Z">Ctrl+Z</button>
                <button class="keyboard-key shortcut" data-keys="CTRL+A">Ctrl+A</button>
                <button class="keyboard-key shortcut" data-keys="CTRL+S">Ctrl+S</button>
                <button class="keyboard-key shortcut" data-keys="ALT+TAB">Alt+Tab</button>
                <button class="keyboard-key shortcut" data-keys="CTRL+SHIFT+ESC">TaskMgr</button>
                <button class="keyboard-key shortcut" data-keys="CTRL+ALT+DEL">Ctrl+Alt+Del</button>
                <button class="keyboard-key shortcut" data-keys="WIN+L">Win+L</button>
                <button class="keyboard-key shortcut" data-keys="WIN+R">Win+R</button>
              </div>
            </div>
          </div>

          <!-- Sound Popup Menu -->
          <div class="popup-menu sound-menu" id="sound-menu">
            <div class="popup-header">
              <div class="popup-title">Sound Mixer</div>
              <button class="popup-close" aria-label="Close">
                <ha-icon icon="mdi:close"></ha-icon>
              </button>
            </div>
            <div class="popup-content">
              <div class="sound-section">
                <div class="sound-label">Master Volume</div>
                <div class="volume-control">
                  <input type="range" id="master-volume-slider" min="0" max="100" value="${masterVolume}" 
                         class="volume-slider" aria-label="Master Volume">
                  <span class="volume-value">${masterVolume}%</span>
                </div>
              </div>

              <div class="sound-section">
                <div class="sound-label">Output Device</div>
                <select id="output-device-select" class="device-select" aria-label="Output Device">
                  ${audioDevices.map(device => `
                    <option value="${this._escapeHtml(device.id)}" ${device.id === defaultDeviceId ? 'selected' : ''}>
                      ${this._escapeHtml(device.name || device.id)}
                    </option>
                  `).join('')}
                </select>
              </div>

              <div class="sound-section">
                <div class="sound-label">Application Volumes</div>
                <div class="app-volumes">
                  ${audioApps.length > 0 ? audioApps.map(app => `
                    <div class="app-volume-item">
                      <div class="app-name">${this._escapeHtml(app.name || `Process ${app.process_id}`)}</div>
                      <div class="volume-control">
                        <input type="range" class="app-volume-slider" 
                               data-process-id="${app.process_id}"
                               min="0" max="100" 
                               value="${Math.round((app.volume || 0) * 100)}" 
                               aria-label="Volume for ${this._escapeHtml(app.name || 'app')}">
                        <span class="volume-value">${Math.round((app.volume || 0) * 100)}%</span>
                      </div>
                      ${audioDevices && audioDevices.length > 0 ? `
                        <select class="app-device-select" data-process-id="${app.process_id}" aria-label="Device for ${this._escapeHtml(app.name || 'app')}">
                          ${audioDevices.map(device => `
                            <option value="${this._escapeHtml(device.id)}" ${device.id === app.device_id ? 'selected' : ''}>
                              ${this._escapeHtml(device.name || device.id)}
                            </option>
                          `).join('')}
                        </select>
                      ` : ''}
                    </div>
                  `).join('') : '<div class="no-apps">No audio applications running</div>'}
                </div>
              </div>
            </div>
          </div>
        </div>
      </ha-card>
    `;

    this.attachEventHandlers();
    this.setupScreenInteraction();
    if (isOnline) {
      this.setupTouchpadMode();
    }
  }

  getBaseUrlFromEntity(entity) {
    const attrs = entity.attributes || {};
    if (attrs.base_url) return attrs.base_url;
    
    if (this._hass.config_entries && this._hass.config_entries.entries) {
      const configEntry = this._hass.config_entries.entries.find(
        e => e.domain === 'opencrol' && (e.title?.includes(attrs.client_id || '') || e.title?.includes(entity.entity_id))
      );
      if (configEntry?.data?.host) {
        const port = configEntry.data.port || 8080;
        const protocol = configEntry.data.use_https ? 'https' : 'http';
        return `${protocol}://${configEntry.data.host}:${port}`;
      }
    }
    
    return null;
  }

  setupTouchpadMode() {
    const touchpadArea = this.querySelector('#touchpad-area');
    // Only setup if touchpad exists and is visible (not hidden)
    if (!touchpadArea || touchpadArea.classList.contains('hidden')) return;
    
    // Prevent duplicate event listeners by checking if already set up
    if (touchpadArea.dataset.touchpadSetup === 'true') return;
    touchpadArea.dataset.touchpadSetup = 'true';

    let isDown = false;
    let lastX = null;
    let lastY = null;
    let startX = null;
    let startY = null;

    // Mouse events
    touchpadArea.addEventListener('mousedown', (e) => {
      e.preventDefault();
      isDown = true;
      lastX = e.clientX;
      lastY = e.clientY;
      startX = e.clientX;
      startY = e.clientY;
      touchpadArea.classList.add('active');
    });

    touchpadArea.addEventListener('mousemove', (e) => {
      e.preventDefault();
      if (isDown && lastX !== null && lastY !== null) {
        const deltaX = e.clientX - lastX;
        const deltaY = e.clientY - lastY;
        
        if (Math.abs(deltaX) > 2 || Math.abs(deltaY) > 2) {
          this.sendCommand('move_mouse', { 
            x: Math.round(deltaX * 1.5),
            y: Math.round(deltaY * 1.5),
            relative: true
          });
          lastX = e.clientX;
          lastY = e.clientY;
        }
      }
    });

    touchpadArea.addEventListener('mouseup', (e) => {
      e.preventDefault();
      touchpadArea.classList.remove('active');
      if (isDown && startX !== null && startY !== null) {
        const delta = Math.abs(e.clientX - startX) + Math.abs(e.clientY - startY);
        if (delta < 5) {
          this.sendCommand('click', { button: 'left' });
        }
      }
      isDown = false;
      lastX = null;
      lastY = null;
      startX = null;
      startY = null;
    });

    touchpadArea.addEventListener('contextmenu', (e) => {
      e.preventDefault();
      this.sendCommand('click', { button: 'right' });
    });

    touchpadArea.addEventListener('wheel', (e) => {
      e.preventDefault();
      const delta = Math.round(e.deltaY);
      if (delta !== 0) {
        this.sendCommand('scroll', { delta: delta });
      }
    });

    // Touch events
    let touchStartX = null;
    let touchStartY = null;
    let touchStartTime = null;

    touchpadArea.addEventListener('touchstart', (e) => {
      e.preventDefault();
      const touch = e.touches[0];
      touchStartX = touch.clientX;
      touchStartY = touch.clientY;
      touchStartTime = Date.now();
      lastX = touch.clientX;
      lastY = touch.clientY;
      isDown = true;
      touchpadArea.classList.add('active');
    });

    touchpadArea.addEventListener('touchmove', (e) => {
      e.preventDefault();
      if (e.touches.length === 1 && isDown && lastX !== null && lastY !== null) {
        const touch = e.touches[0];
        const deltaX = touch.clientX - lastX;
        const deltaY = touch.clientY - lastY;
        
        if (Math.abs(deltaX) > 2 || Math.abs(deltaY) > 2) {
          this.sendCommand('move_mouse', { 
            x: Math.round(deltaX * 1.5),
            y: Math.round(deltaY * 1.5),
            relative: true
          });
          lastX = touch.clientX;
          lastY = touch.clientY;
        }
      } else if (e.touches.length === 2) {
        // Two-finger scroll
        const touch1 = e.touches[0];
        const touch2 = e.touches[1];
        const deltaY = (touch1.clientY + touch2.clientY) / 2 - (lastY || touch1.clientY);
        if (Math.abs(deltaY) > 5) {
          this.sendCommand('scroll', { delta: Math.round(deltaY) });
          lastY = (touch1.clientY + touch2.clientY) / 2;
        }
      }
    });

    touchpadArea.addEventListener('touchend', (e) => {
      e.preventDefault();
      touchpadArea.classList.remove('active');
      if (touchStartX !== null && touchStartY !== null) {
        const touch = e.changedTouches[0];
        const delta = Math.abs(touch.clientX - touchStartX) + Math.abs(touch.clientY - touchStartY);
        const duration = Date.now() - touchStartTime;
        
        if (delta < 10 && duration < 300) {
          this.sendCommand('click', { button: 'left' });
        }
      }
      isDown = false;
      lastX = null;
      lastY = null;
      touchStartX = null;
      touchStartY = null;
    });
  }

  setupScreenInteraction() {
    const screenOverlay = this.querySelector('#screen-overlay');
    const screenImg = this.querySelector('#screen-stream');
    const touchpadArea = this.querySelector('#touchpad-area');
    const screenContainer = this.querySelector('#touchpad-container');
    
    if (!screenImg || !screenOverlay) {
      if (touchpadArea) {
        touchpadArea.classList.remove('hidden');
      }
      return;
    }

    this._imgElement = screenImg;

    // Click handling
    screenOverlay.addEventListener('click', (e) => {
      if (e.target === screenOverlay || e.target.classList.contains('screen-overlay')) {
        const rect = screenImg.getBoundingClientRect();
        const x = Math.round((e.clientX - rect.left) * (screenImg.naturalWidth / rect.width));
        const y = Math.round((e.clientY - rect.top) * (screenImg.naturalHeight / rect.height));
        this.sendCommand('click', { button: 'left', x: x, y: y });
      }
    });

    screenOverlay.addEventListener('contextmenu', (e) => {
      e.preventDefault();
      const rect = screenImg.getBoundingClientRect();
      const x = Math.round((e.clientX - rect.left) * (screenImg.naturalWidth / rect.width));
      const y = Math.round((e.clientY - rect.top) * (screenImg.naturalHeight / rect.height));
      this.sendCommand('click', { button: 'right', x: x, y: y });
    });

    // Mouse movement
    let isDragging = false;
    screenOverlay.addEventListener('mousedown', () => { isDragging = true; });
    screenOverlay.addEventListener('mouseup', () => { isDragging = false; });
    screenOverlay.addEventListener('mousemove', (e) => {
      if (isDragging) {
        const rect = screenImg.getBoundingClientRect();
        const x = Math.round((e.clientX - rect.left) * (screenImg.naturalWidth / rect.width));
        const y = Math.round((e.clientY - rect.top) * (screenImg.naturalHeight / rect.height));
        this.sendCommand('move_mouse', { x: x, y: y });
      }
    });

    screenOverlay.addEventListener('wheel', (e) => {
      e.preventDefault();
      this.sendCommand('scroll', { delta: Math.round(e.deltaY) });
    });

    // Always setup touchpad first
    if (touchpadArea) {
      this.setupTouchpadMode();
    }

    // Stream load handlers
    screenImg.addEventListener('load', () => {
      if (screenImg.naturalWidth > 0 && screenImg.naturalHeight > 0) {
        screenImg.style.display = 'block';
        screenOverlay.style.display = 'block';
        const fullscreenBtn = this.querySelector('.fullscreen-btn');
        if (fullscreenBtn) fullscreenBtn.style.display = 'flex';
        if (touchpadArea) touchpadArea.classList.add('hidden');
      }
    });
    
    screenImg.addEventListener('error', () => {
      screenImg.style.display = 'none';
      screenOverlay.style.display = 'none';
      const fullscreenBtn = this.querySelector('.fullscreen-btn');
      if (fullscreenBtn) fullscreenBtn.style.display = 'none';
      if (touchpadArea) touchpadArea.classList.remove('hidden');
    });
    
    // Try to start screen capture if online (stream endpoint auto-starts capture)
    const entityForCapture = this._hass.states[this.config.entity];
    const attrsForCapture = entityForCapture?.attributes || {};
    const statusForCapture = attrsForCapture.status || 'offline';
    const isOnlineForCapture = statusForCapture === 'online';
    const isCaptureActiveForCapture = attrsForCapture.screen_capture_active || false;
    const currentMonitorForCapture = attrsForCapture.current_monitor !== undefined ? attrsForCapture.current_monitor : 0;
    
    if (isOnlineForCapture && this.config.entity && screenImg) {
      // The stream endpoint auto-starts capture when accessed, but we call start_screen_capture
      // to ensure status is updated correctly
      if (!isCaptureActiveForCapture) {
        setTimeout(() => {
          this._hass.callService('opencrol', 'start_screen_capture', {
            entity_id: this.config.entity,
          }).then(() => {
            // Refresh stream after starting capture
            setTimeout(() => {
              if (screenImg && this._screenStreamUrl) {
                const baseUrl = this._screenStreamUrl.split('?')[0];
                const monitorPart = this._screenStreamUrl.includes('monitor=') 
                  ? this._screenStreamUrl.split('monitor=')[1].split('&')[0]
                  : currentMonitorForCapture;
                screenImg.src = `${baseUrl}?monitor=${monitorPart}&_t=${Date.now()}`;
              }
            }, 800);
          }).catch(err => {
            console.error('Failed to start screen capture:', err);
          });
        }, 300);
      } else {
        // Already active, refresh stream URL to get latest frames
        if (screenImg && this._screenStreamUrl) {
          const baseUrl = this._screenStreamUrl.split('?')[0];
          const monitorPart = this._screenStreamUrl.includes('monitor=') 
            ? this._screenStreamUrl.split('monitor=')[1].split('&')[0]
            : currentMonitorForCapture;
          screenImg.src = `${baseUrl}?monitor=${monitorPart}&_t=${Date.now()}`;
        }
      }
    }
    
    // Check if image already loaded
    if (screenImg && screenImg.complete && screenImg.naturalWidth > 0 && screenImg.naturalHeight > 0) {
      screenImg.dispatchEvent(new Event('load'));
    }

    // Fullscreen button
    const fullscreenBtn = this.querySelector('.fullscreen-btn');
    if (fullscreenBtn) {
      fullscreenBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        const entityForFullscreen = this._hass.states[this.config.entity];
        const attrsForFullscreen = entityForFullscreen?.attributes || {};
        const baseUrl = this.config.base_url || this.getBaseUrlFromEntity(entityForFullscreen);
        const currentMonitor = attrsForFullscreen.current_monitor !== undefined ? attrsForFullscreen.current_monitor : 0;
        this.openFullscreenRemote(baseUrl, currentMonitor);
      });
    }
  }

  attachEventHandlers() {
    // Power buttons
    const powerOnBtn = this.querySelector('#power-on-btn');
    if (powerOnBtn) {
      powerOnBtn.addEventListener('click', () => {
        const mediaEntityId = this.config.entity.replace('remote.', 'media_player.').replace('_remote', '_screen');
        if (this._hass.states[mediaEntityId]) {
          this._hass.callService('media_player', 'turn_on', { entity_id: mediaEntityId }).catch(() => {
            this.sendCommand('start_screen_capture');
          });
        } else {
          this.sendCommand('start_screen_capture');
        }
      });
    }

    const powerOffBtn = this.querySelector('#power-off-btn');
    if (powerOffBtn) {
      powerOffBtn.addEventListener('click', () => {
        const mediaEntityId = this.config.entity.replace('remote.', 'media_player.').replace('_remote', '_screen');
        if (this._hass.states[mediaEntityId]) {
          this._hass.callService('media_player', 'turn_off', { entity_id: mediaEntityId }).catch(() => {
            this.sendCommand('stop_screen_capture');
          });
        } else {
          this.sendCommand('stop_screen_capture');
        }
      });
    }

    // Lock button
    const lockBtn = this.querySelector('#lock-btn');
    if (lockBtn) {
      lockBtn.addEventListener('click', () => {
        this.sendCommand('lock');
      });
    }

    // Monitor buttons
    this.querySelectorAll('.monitor-icon').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        e.preventDefault();
        const index = parseInt(btn.dataset.monitorIndex);
        if (!isNaN(index) && this.config.entity) {
          this._hass.callService('opencrol', 'select_monitor', {
            entity_id: this.config.entity,
            monitor_index: index,
          }).catch(() => {});
          
          this._hass.callService('opencrol', 'start_screen_capture', {
            entity_id: this.config.entity,
          }).catch(() => {});

          // Update stream URL with new monitor
          const entityForStream = this._hass.states[this.config.entity];
          const attrsForStream = entityForStream?.attributes || {};
          const baseUrl = this.config.base_url || this.getBaseUrlFromEntity(entityForStream);
          if (baseUrl) {
            const newStreamUrl = `${baseUrl}/api/v1/screenstream/stream?monitor=${index}`;
            this._screenStreamUrl = newStreamUrl;
            const screenImg = this.querySelector('#screen-stream');
            if (screenImg) {
              screenImg.src = `${newStreamUrl}&_t=${Date.now()}`;
            }
          }
        }
      });
    });

    // Menu toggles
    const soundBtn = this.querySelector('#sound-btn');
    const keyboardBtn = this.querySelector('#keyboard-btn');
    const soundMenu = this.querySelector('#sound-menu');
    const keyboardMenu = this.querySelector('#keyboard-menu');

    if (soundBtn && soundMenu) {
      soundBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        e.preventDefault();
        const isOpen = soundMenu.classList.contains('open');
        if (isOpen) {
          soundMenu.classList.remove('open');
        } else {
          soundMenu.classList.add('open');
          if (keyboardMenu) keyboardMenu.classList.remove('open');
        }
      });
    }

    if (keyboardBtn && keyboardMenu) {
      keyboardBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        e.preventDefault();
        const isOpen = keyboardMenu.classList.contains('open');
        if (isOpen) {
          keyboardMenu.classList.remove('open');
        } else {
          keyboardMenu.classList.add('open');
          if (soundMenu) soundMenu.classList.remove('open');
          const textInput = this.querySelector('#text-input');
          if (textInput) setTimeout(() => textInput.focus(), 100);
        }
      });
    }

    // Close buttons
    this.querySelectorAll('.popup-close').forEach(btn => {
      btn.addEventListener('click', () => {
        this.querySelectorAll('.popup-menu').forEach(menu => menu.classList.remove('open'));
      });
    });

    // Close on outside click (only add once)
    if (!this._outsideClickHandler) {
      this._outsideClickHandler = (e) => {
        if (!this.contains(e.target)) {
          this.querySelectorAll('.popup-menu').forEach(menu => menu.classList.remove('open'));
        }
      };
      document.addEventListener('click', this._outsideClickHandler);
    }

    // Type text
    const typeBtn = this.querySelector('#type-btn');
    const textInput = this.querySelector('#text-input');
    if (typeBtn && textInput) {
      typeBtn.addEventListener('click', () => {
        if (textInput.value.trim()) {
          this.sendCommand('type_text', { text: textInput.value });
          textInput.value = '';
        }
      });
      textInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
          e.preventDefault();
          typeBtn.click();
        }
      });
    }

    // Keyboard keys
    this._activeModifiers = this._activeModifiers || new Set();

    const updateModifierStyles = () => {
      this.querySelectorAll('.keyboard-key.toggle').forEach(btn => {
        const key = (btn.dataset.key || '').toUpperCase();
        if (this._activeModifiers.has(key)) {
          btn.classList.add('toggled');
        } else {
          btn.classList.remove('toggled');
        }
      });
    };

    this.querySelectorAll('.keyboard-key').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        e.preventDefault();
        
        const key = (btn.dataset.key || '').toUpperCase();
        const combo = btn.dataset.keys;

        if (combo) {
          this.sendCommand('send_key', { keys: combo });
          this._activeModifiers.clear();
          updateModifierStyles();
          return;
        }

        if (!key) return;

        const isToggle = btn.classList.contains('toggle');
        if (isToggle && key) {
          if (this._activeModifiers.has(key)) {
            this._activeModifiers.delete(key);
          } else {
            this._activeModifiers.add(key);
          }
          updateModifierStyles();
        } else if (key) {
          const mods = Array.from(this._activeModifiers);
          const parts = mods.length > 0 ? [...mods, key] : [key];
          const keysString = parts.join('+');
          this.sendCommand('send_key', { keys: keysString });
          this._activeModifiers.clear();
          updateModifierStyles();
        }
      });
    });

    // Volume controls
    const masterVolumeSlider = this.querySelector('#master-volume-slider');
    if (masterVolumeSlider) {
      let volumeTimeout;
      masterVolumeSlider.addEventListener('input', (e) => {
        const value = parseInt(e.target.value);
        const valueDisplay = masterVolumeSlider.nextElementSibling;
        if (valueDisplay) valueDisplay.textContent = value + '%';
        
        clearTimeout(volumeTimeout);
        volumeTimeout = setTimeout(() => {
          this.sendCommand('set_volume', { volume: value / 100 });
        }, 100);
      });
    }

    // App volume sliders
    this.querySelectorAll('.app-volume-slider').forEach(slider => {
      let volumeTimeout;
      slider.addEventListener('input', (e) => {
        const value = parseInt(e.target.value);
        const processId = parseInt(e.target.dataset.processId);
        const valueDisplay = e.target.nextElementSibling;
        if (valueDisplay) valueDisplay.textContent = value + '%';
        
        clearTimeout(volumeTimeout);
        volumeTimeout = setTimeout(() => {
          this.sendCommand('set_app_volume', { process_id: processId, volume: value / 100 });
        }, 100);
      });
    });

    // Device selectors
    const outputDeviceSelect = this.querySelector('#output-device-select');
    if (outputDeviceSelect) {
      outputDeviceSelect.addEventListener('change', async (e) => {
        const deviceId = e.target.value;
        if (!deviceId) return;
        
        try {
          // Call the service directly to get better error feedback
          const result = await this._hass.callService('opencrol', 'set_default_device', {
            entity_id: this.config.entity,
            device_id: deviceId
          });
          
          // Log result for debugging
          if (result && typeof result === 'object') {
            if (result.warning) {
              console.warn('Device selection warning:', result.warning);
              console.warn('Requested:', result.requested_device, 'Current:', result.current_default);
            }
          }
        } catch (err) {
          console.error('Failed to set default audio device:', err);
          // Revert selection on error
          const entity = this._hass.states[this.config.entity];
          const devices = entity?.attributes?.audio_devices || [];
          const currentDefault = devices.find(d => d.is_default)?.id;
          if (currentDefault && outputDeviceSelect) {
            outputDeviceSelect.value = currentDefault;
          }
        }
      });
    }

    this.querySelectorAll('.app-device-select').forEach(select => {
      select.addEventListener('change', (e) => {
        const processId = parseInt(e.target.dataset.processId);
        this.sendCommand('set_app_device', { process_id: processId, device_id: e.target.value });
      });
    });
  }

  openFullscreenRemote(baseUrl, monitorIndex = 0) {
    if (this._isFullscreenOpen) {
      this.closeFullscreenRemote();
      return;
    }

    const entity = this._hass.states[this.config.entity];
    const attributes = entity?.attributes || {};
    const clientId = attributes.client_id || entity?.attributes?.friendly_name || this.config.entity;
    const monitorParam = monitorIndex >= 0 ? `?monitor=${monitorIndex}` : '';
    const streamUrl = `${baseUrl}/api/v1/screenstream/stream${monitorParam}`;

    this._isFullscreenOpen = true;
    this._fullscreenOverlay = document.createElement('div');
    this._fullscreenOverlay.className = 'fullscreen-overlay';
    this._fullscreenOverlay.innerHTML = `
      <div class="fullscreen-header">
        <div class="fullscreen-title">${this._escapeHtml(clientId)} - Fullscreen Remote</div>
        <button class="fullscreen-close" aria-label="Close Fullscreen">
          <ha-icon icon="mdi:close"></ha-icon>
        </button>
      </div>
      <div class="fullscreen-content">
        <img src="${streamUrl}" alt="Screen Stream" class="fullscreen-stream">
      </div>
    `;

    document.body.appendChild(this._fullscreenOverlay);

    const closeBtn = this._fullscreenOverlay.querySelector('.fullscreen-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => this.closeFullscreenRemote());
    }

    const streamImg = this._fullscreenOverlay.querySelector('.fullscreen-stream');
    if (streamImg) {
      this.setupFullscreenInteraction(streamImg, baseUrl);
    }
  }

  closeFullscreenRemote() {
    if (this._fullscreenOverlay) {
      this._fullscreenOverlay.remove();
      this._fullscreenOverlay = null;
      this._isFullscreenOpen = false;
    }
  }

  setupFullscreenInteraction(img, baseUrl) {
    img.addEventListener('click', (e) => {
      const rect = img.getBoundingClientRect();
      const x = Math.round((e.clientX - rect.left) * (img.naturalWidth / rect.width));
      const y = Math.round((e.clientY - rect.top) * (img.naturalHeight / rect.height));
      this.sendCommand('click', { button: 'left', x: x, y: y });
    });

    img.addEventListener('contextmenu', (e) => {
      e.preventDefault();
      const rect = img.getBoundingClientRect();
      const x = Math.round((e.clientX - rect.left) * (img.naturalWidth / rect.width));
      const y = Math.round((e.clientY - rect.top) * (img.naturalHeight / rect.height));
      this.sendCommand('click', { button: 'right', x: x, y: y });
    });

    img.addEventListener('wheel', (e) => {
      e.preventDefault();
      this.sendCommand('scroll', { delta: Math.round(e.deltaY) });
    });

    let isDragging = false;
    img.addEventListener('mousedown', () => { isDragging = true; });
    img.addEventListener('mouseup', () => { isDragging = false; });
    img.addEventListener('mousemove', (e) => {
      if (isDragging) {
        const rect = img.getBoundingClientRect();
        const x = Math.round((e.clientX - rect.left) * (img.naturalWidth / rect.width));
        const y = Math.round((e.clientY - rect.top) * (img.naturalHeight / rect.height));
        this.sendCommand('move_mouse', { x: x, y: y });
      }
    });
  }

  sendCommand(service, data = {}) {
    if (!this.config?.entity || !this._hass) return;
    
    const entityId = this.config.entity;
    this._hass.callService('opencrol', service, {
      entity_id: entityId,
      ...data
    }).catch(err => {
      console.error(`OpenCtrol card: Error calling service ${service}:`, err);
    });
  }

  _escapeHtml(text) {
    if (text == null) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
}

// Define the custom element BEFORE registration
if (!customElements.get('opencrol-remote-card')) {
  customElements.define('opencrol-remote-card', OpenCtrolRemoteCard);
}

// Card registration for Home Assistant card picker
window.customCards = window.customCards || [];
const cardAlreadyRegistered = window.customCards.some(
  card => card.type === 'custom:opencrol-remote-card'
);

if (!cardAlreadyRegistered) {
  window.customCards.push({
    type: 'custom:opencrol-remote-card',
    name: 'OpenCtrol Remote',
    description: 'Remote control card for OpenCtrol devices with screen streaming and touchpad support',
    preview: true,
    documentationURL: 'https://github.com/Kaando2000/opencrol-integration',
    author: 'Kaando2000'
  });
  console.log('OpenCtrol Remote card registered:', {
    type: 'custom:opencrol-remote-card',
    element: 'opencrol-remote-card',
    customCards: window.customCards.length
  });
} else {
  console.log('OpenCtrol Remote card already registered');
}

if (window.loadCardHelpers) {
  window.loadCardHelpers().then(({ createCardElement }) => {
    console.log('OpenCtrol Remote card loaded successfully');
  }).catch(err => {
    console.error('Error loading OpenCtrol card helpers:', err);
  });
}

})(); // End IIFE
