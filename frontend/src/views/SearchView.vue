<template>
  <div id="search-page-container" ref="searchContainer"></div>
</template>

<script>
export default {
  name: 'SearchView',
  data() {
    return {
      searchHtml: '',
      isLoading: true,
      originalBodyStyle: null
    };
  },
  async mounted() {
    this.originalBodyStyle = document.body.style.cssText;
    document.body.style.background = '#ffffff';
    document.body.style.backgroundColor = '#ffffff';
    await this.loadSearchHtml();
  },
  beforeUnmount() {
    if (this.originalBodyStyle !== null) {
      document.body.style.cssText = this.originalBodyStyle;
    }
  },
  methods: {
    async loadSearchHtml() {
      try {
        let htmlUrl = '/search.html';
        if (window.location.port === '5173' || window.location.port === '4173') {
          htmlUrl = '/search.html';
        }

        const response = await fetch(htmlUrl);
        if (!response.ok) {
          throw new Error(`Failed to load search.html: ${response.status}`);
        }

        this.searchHtml = await response.text();
        this.$nextTick(() => {
          this.injectSearchPage();
        });
      } catch (error) {
        console.error('Error loading search page:', error);
        this.$refs.searchContainer.innerHTML = `
          <div style="padding: 40px; text-align: center; color: #666;">
            <h2>搜索页面加载失败</h2>
            <p>${error.message}</p>
          </div>
        `;
      }
    },
    injectSearchPage() {
      const container = this.$refs.searchContainer;
      if (!container) return;

      const tempDiv = document.createElement('div');
      tempDiv.innerHTML = this.searchHtml;

      const style = tempDiv.querySelector('style');
      if (style) {
        const newStyle = document.createElement('style');
        newStyle.textContent = style.textContent;
        document.head.appendChild(newStyle);
      }

      const bodyContent = tempDiv.querySelector('body');
      if (bodyContent) {
        container.innerHTML = bodyContent.innerHTML;
      } else {
        container.innerHTML = tempDiv.innerHTML;
      }

      this.$nextTick(() => {
        this.executeSearchScripts();
      });
    },
    executeSearchScripts() {
      const searchQuery = this.getUrlParameter('q');
      const resultsContainer = document.getElementById('resultsContainer');
      const searchInput = document.getElementById('searchInput');

      if (searchQuery && searchInput) {
        searchInput.value = searchQuery;
        this.performSearch(searchQuery);
      }

      const searchForm = document.getElementById('searchForm');
      if (searchForm) {
        searchForm.addEventListener('submit', (e) => {
          e.preventDefault();
          const query = searchInput.value.trim();
          if (query.length > 0) {
            this.$router.push(`/search?q=${encodeURIComponent(query)}`);
            this.performSearch(query);
          }
        });
      }
    },
    getUrlParameter(name) {
      const url = new URL(window.location);
      return url.searchParams.get(name);
    },
    getApiBase() {
      if (window.location.port === '5173' || window.location.port === '4173') {
        return 'http://127.0.0.1:8000';
      }
      return window.location.origin;
    },
    getFrontendBase() {
      if (window.location.port === '8000') {
        return 'http://127.0.0.1:5173';
      }
      return window.location.origin;
    },
    toFrontendUrl(pathOrUrl) {
      if (!pathOrUrl) {
        return '#';
      }
      if (/^https?:\/\//i.test(pathOrUrl)) {
        return pathOrUrl;
      }
      const path = pathOrUrl.startsWith('/') ? pathOrUrl : `/${pathOrUrl}`;
      return `${this.getFrontendBase()}${path}`;
    },
    async performSearch(query) {
      const resultsContainer = document.getElementById('resultsContainer');
      if (!query || query.trim().length === 0) {
        if (resultsContainer) resultsContainer.innerHTML = '';
        return;
      }

      if (resultsContainer) {
        resultsContainer.innerHTML = '<div class="loading">Searching...</div>';
      }

      const apiUrl = `${this.getApiBase()}/api/v1/search?q=${encodeURIComponent(query)}&limit=50`;

      try {
        const response = await fetch(apiUrl, {
          headers: {
            'Accept': 'application/json'
          }
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const contentType = response.headers.get('content-type') || '';
        if (!contentType.toLowerCase().includes('application/json')) {
          throw new Error(`Expected JSON response, got ${contentType}`);
        }

        const data = await response.json();
        this.displayResults(data);
      } catch (error) {
        if (resultsContainer) {
          resultsContainer.innerHTML = `
            <div class="error">
              <strong>Search Error:</strong> ${error.message}
            </div>
          `;
        }
      }
    },
    displayResults(data) {
      const resultsContainer = document.getElementById('resultsContainer');
      if (!resultsContainer) return;

      let html = '';

      html += `<div class="info-box">`;
      html += `Found <strong>${data.total_results} results</strong> for "<strong>${this.escapeHtml(data.query)}</strong>"`;
      if (data.total_results > 0) {
        html += ` (displaying ${Math.min(data.results.length, data.total_results)})`;
      }
      html += `</div>`;

      if (data.results.length === 0) {
        html += `
          <div class="no-results">
            <p>No results found for "<strong>${this.escapeHtml(data.query)}</strong>"</p>
            <p style="font-size: 11px; color: #999999;">
              Try different keywords or check our services above.
            </p>
          </div>
        `;
      } else {
        html += '<div class="results">';
        data.results.forEach(result => {
          html += this.formatResultItem(result);
        });
        html += '</div>';
      }

      resultsContainer.innerHTML = html;
    },
    formatResultItem(result) {
      const contentTypeLabel = this.getContentTypeLabel(result.content_type);
      const relevancePercent = Math.round(result.relevance_score * 100);
      const resultUrl = this.toFrontendUrl(result.url);

      let html = '<div class="result-item">';

      html += `<div class="result-title">`;
      html += `<a href="${this.escapeHtml(resultUrl)}" target="_blank">${this.escapeHtml(result.title)}</a>`;
      html += `</div>`;

      html += `<div class="result-url">${this.escapeHtml(resultUrl)}</div>`;

      html += `<div class="result-meta">`;
      html += `<span class="result-type">${contentTypeLabel}</span>`;
      html += `<span>Relevance: ${relevancePercent}%</span>`;
      if (result.metadata && result.metadata.price) {
        html += ` | Price: $${result.metadata.price}`;
      }
      if (result.metadata && result.metadata.category) {
        html += ` | Category: ${this.escapeHtml(result.metadata.category)}`;
      }
      html += `</div>`;

      html += `<div class="result-snippet">`;
      html += this.escapeHtml(this.truncateText(result.description, 150));
      html += `</div>`;

      html += `<div class="result-meta">`;
      html += `Last updated: ${this.formatDate(result.created_at)}`;
      html += `</div>`;

      html += '</div>';

      return html;
    },
    getContentTypeLabel(contentType) {
      const labels = {
        'forum_thread': 'Forum Thread',
        'forum_post': 'Forum Post',
        'product': 'Product',
        'order': 'Order',
        'news': 'News Article',
        'page': 'Web Page',
        'netdisk_file': 'File'
      };
      return labels[contentType] || contentType;
    },
    escapeHtml(text) {
      const div = document.createElement('div');
      div.textContent = text;
      return div.innerHTML;
    },
    truncateText(text, maxLength) {
      if (text.length <= maxLength) return text;
      return text.substring(0, maxLength).trim() + '...';
    },
    formatDate(isoString) {
      try {
        const date = new Date(isoString);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
      } catch {
        return isoString;
      }
    }
  }
};
</script>

<style scoped>
#search-page-container {
  width: 100%;
  min-height: 100vh;
}
</style>
