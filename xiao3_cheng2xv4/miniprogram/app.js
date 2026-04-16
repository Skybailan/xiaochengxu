const DEFAULT_OPEN_ID = 'demo-openid-001';
const STORAGE_KEYS = {
  reviewCache: 'word-memory-review-cache',
};

function safeReadStorage(key, fallbackValue) {
  try {
    const value = wx.getStorageSync(key);
    return value || fallbackValue;
  } catch (error) {
    return fallbackValue;
  }
}

function safeWriteStorage(key, value) {
  try {
    wx.setStorageSync(key, value);
  } catch (error) {
    console.warn(`storage write failed: ${key}`, error);
  }
}

App({
  onLaunch() {
    const storedReviewCache = safeReadStorage(STORAGE_KEYS.reviewCache, null);

    this.globalData = {
      env: '',
      apiBaseUrl: 'https://django-ij21-247043-8-1422675813.sh.run.tcloudbase.com/api',
      openid: DEFAULT_OPEN_ID,
      storageKeys: STORAGE_KEYS,
      reviewCache: storedReviewCache || {
        daily: null,
        pro: null,
      },
    };

    if (wx.cloud) {
      wx.cloud.init({
        env: this.globalData.env,
        traceUser: true,
      });
    }
  },

  getReviewCache(mode) {
    const reviewCache = this.globalData.reviewCache || { daily: null, pro: null };
    return reviewCache[mode] || null;
  },

  setReviewCache(mode, payload) {
    const reviewCache = this.globalData.reviewCache || { daily: null, pro: null };
    const nextReviewCache = {
      ...reviewCache,
      [mode]: payload,
    };
    this.globalData.reviewCache = nextReviewCache;
    safeWriteStorage(STORAGE_KEYS.reviewCache, nextReviewCache);
  },

  clearReviewCache(mode) {
    const reviewCache = this.globalData.reviewCache || { daily: null, pro: null };
    const nextReviewCache = {
      ...reviewCache,
      [mode]: null,
    };
    this.globalData.reviewCache = nextReviewCache;
    safeWriteStorage(STORAGE_KEYS.reviewCache, nextReviewCache);
  },
});
