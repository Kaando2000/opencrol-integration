// OpenCtrol Remote Card for Home Assistant Lovelace
// Version: 2.0.0
// Auto-loaded by OpenCtrol Integration

// Load CSS
const link = document.createElement('link');
link.rel = 'stylesheet';
link.type = 'text/css';
link.href = '/local/opencrol/opencrol-remote-card.css';
document.head.appendChild(link);

class OpenCtrolRemoteCard extends HTMLElement {
  constructor() {
    super();
    this._screenStreamUrl = null;
    this._imgElement = null;
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
  }

  disconnectedCallback() {
    // Stop screen stream when card is removed
    if (this._imgElement) {
      this._imgElement.src = '';
      this._imgElement = null;
    }
  }

  updateCard() {
    if (!this.config || !this._hass) return;

    const entity = this._hass.states[this.config.entity];
    if (!entity) {
      this.innerHTML = '<ha-card><div class="error">Entity not found</div></ha-card>';
      return;
    }

    const state = entity.state;
    const attributes = entity.attributes || {};
    const isOnline = state === 'on' || state === 'online';
    
    // Get base URL from entity attributes or config
    const baseUrl = this.config.base_url || this.getBaseUrlFromEntity(entity);
    this._screenStreamUrl = baseUrl ? `${baseUrl}/api/v1/screenstream/stream` : null;

    this.innerHTML = `
      <ha-card>
        <div class="card-header">
          <div class="name">${entity.attributes.friendly_name || this.config.entity}</div>
          <div class="status ${isOnline ? 'online' : 'offline'}">${isOnline ? 'Online' : 'Offline'}</div>
        </div>
        <div class="card-content">
          ${isOnline && this._screenStreamUrl ? `
            <div class="screen-container">
              <img id="screen-stream" 
                   src="${this._screenStreamUrl}" 
                   alt="Screen Stream"
                   class="screen-view">
              <div class="screen-overlay" id="screen-overlay"></div>
            </div>
          ` : `
            <div class="screen-placeholder">
              <div class="placeholder-text">${isOnline ? 'Screen stream unavailable' : 'Device offline'}</div>
            </div>
          `}
          
          <div class="controls-panel">
            <div class="control-section">
              <div class="section-title">Mouse Control</div>
              <div class="button-group">
                <button class="control-btn" data-action="click" data-button="left">Left Click</button>
                <button class="control-btn" data-action="click" data-button="right">Right Click</button>
                <button class="control-btn" data-action="click" data-button="middle">Middle Click</button>
                <button class="control-btn danger" data-action="secure_attention">Ctrl+Alt+Del</button>
              </div>
            </div>

            <div class="control-section">
              <div class="section-title">Keyboard</div>
              <div class="input-group">
                <input type="text" id="text-input" placeholder="Type text here..." class="text-input">
                <button class="control-btn" id="type-btn">Type</button>
              </div>
              <div class="button-group">
                <button class="control-btn small" data-action="send_key" data-key="Enter">Enter</button>
                <button class="control-btn small" data-action="send_key" data-key="Escape">Esc</button>
                <button class="control-btn small" data-action="send_key" data-key="Tab">Tab</button>
                <button class="control-btn small" data-action="send_key" data-keys="Ctrl+C">Ctrl+C</button>
                <button class="control-btn small" data-action="send_key" data-keys="Ctrl+V">Ctrl+V</button>
              </div>
            </div>

            <div class="control-section">
              <div class="section-title">Volume Control</div>
              <div class="volume-control">
                <input type="range" id="volume-slider" min="0" max="100" 
                       value="${Math.round((attributes.master_volume || 0) * 100)}" 
                       class="volume-slider">
                <span id="volume-value" class="volume-value">${Math.round((attributes.master_volume || 0) * 100)}%</span>
              </div>
            </div>

            ${attributes.monitors && attributes.monitors.length > 1 ? `
            <div class="control-section">
              <div class="section-title">Monitor Selection</div>
              <select id="monitor-select" class="monitor-select">
                ${attributes.monitors.map((monitor, index) => `
                  <option value="${index}" ${monitor.primary ? 'selected' : ''}>
                    Monitor ${index + 1}${monitor.primary ? ' (Primary)' : ''} - ${monitor.bounds.width}x${monitor.bounds.height}
                  </option>
                `).join('')}
              </select>
            </div>
            ` : ''}
          </div>
        </div>
      </ha-card>
    `;

    this.attachEventHandlers();
    this.setupScreenInteraction();
  }

  getBaseUrlFromEntity(entity) {
    // Try to extract base URL from entity attributes
    const attrs = entity.attributes || {};
    if (attrs.base_url) return attrs.base_url;
    
    // Try to get from config entry
    const configEntry = this._hass.config_entries?.entries?.find(
      e => e.domain === 'opencrol' && e.title?.includes(attrs.client_id || '')
    );
    if (configEntry?.data?.host) {
      const port = configEntry.data.port || 8080;
      return `http://${configEntry.data.host}:${port}`;
    }
    
    return null;
  }

  setupScreenInteraction() {
    if (!this._screenStreamUrl) return;

    const screenOverlay = this.querySelector('#screen-overlay');
    const screenImg = this.querySelector('#screen-stream');
    
    if (!screenOverlay || !screenImg) return;

    this._imgElement = screenImg;

    // Handle clicks on screen
    screenOverlay.addEventListener('click', (e) => {
      const rect = screenImg.getBoundingClientRect();
      const x = Math.round((e.clientX - rect.left) * (screenImg.naturalWidth / rect.width));
      const y = Math.round((e.clientY - rect.top) * (screenImg.naturalHeight / rect.height));
      
      this.sendCommand('click', { 
        button: 'left', 
        x: x, 
        y: y 
      });
    });

    // Handle right-click
    screenOverlay.addEventListener('contextmenu', (e) => {
      e.preventDefault();
      const rect = screenImg.getBoundingClientRect();
      const x = Math.round((e.clientX - rect.left) * (screenImg.naturalWidth / rect.width));
      const y = Math.round((e.clientY - rect.top) * (screenImg.naturalHeight / rect.height));
      
      this.sendCommand('click', { 
        button: 'right', 
        x: x, 
        y: y 
      });
    });

    // Handle mouse movement for visual feedback
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
  }

  attachEventHandlers() {
    // Volume slider
    const volumeSlider = this.querySelector('#volume-slider');
    if (volumeSlider) {
      volumeSlider.addEventListener('input', (e) => {
        const value = e.target.value;
        const volumeValue = this.querySelector('#volume-value');
        if (volumeValue) {
          volumeValue.textContent = value + '%';
        }
        this.sendCommand('set_volume', { volume: value / 100 });
      });
    }

    // Type text button
    const typeBtn = this.querySelector('#type-btn');
    const textInput = this.querySelector('#text-input');
    if (typeBtn && textInput) {
      typeBtn.addEventListener('click', () => {
        if (textInput.value) {
          this.sendCommand('type_text', { text: textInput.value });
          textInput.value = '';
        }
      });
      textInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
          typeBtn.click();
        }
      });
    }

    // Control buttons
    this.querySelectorAll('.control-btn[data-action]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const action = btn.dataset.action;
        const button = btn.dataset.button;
        const key = btn.dataset.key;
        const keys = btn.dataset.keys;

        if (action === 'click' && button) {
          this.sendCommand('click', { button: button });
        } else if (action === 'secure_attention') {
          this.sendCommand('secure_attention', {});
        } else if (action === 'send_key') {
          if (keys) {
            this.sendCommand('send_key', { keys: keys });
          } else if (key) {
            this.sendCommand('send_key', { key: key });
          }
        }
      });
    });

    // Monitor selector
    const monitorSelect = this.querySelector('#monitor-select');
    if (monitorSelect) {
      monitorSelect.addEventListener('change', (e) => {
        const monitorIndex = parseInt(e.target.value);
        this.sendCommand('select_monitor', { monitor_index: monitorIndex });
      });
    }
  }

  sendCommand(service, data = {}) {
    const entityId = this.config.entity;
    this._hass.callService('opencrol', service, {
      entity_id: entityId,
      ...data
    });
  }
}

customElements.define('opencrol-remote-card', OpenCtrolRemoteCard);

// Card configuration
window.customCards = window.customCards || [];
window.customCards.push({
  type: 'opencrol-remote-card',
  name: 'OpenCtrol Remote',
  description: 'Remote control card for OpenCtrol devices',
  preview: true,
  documentationURL: 'https://github.com/opencrol/integration'
});


