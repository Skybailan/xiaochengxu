const demoTexts = {
  daily: `单词  中文  日常句  句中文
spanish  西班牙语  I am learning Spanish.  我正在学习西班牙语。
sweater  毛衣  This sweater keeps me warm in winter.  这件毛衣让我冬天保暖。
pet  宠物  I have a cute pet dog.  我有一只可爱的宠物狗。`,
  pro: `单词  词性中文  特殊记法  日常句  句中文
compile  v. 编译  com+pile，像把代码堆起来统一处理  I compile the project before release.  我在发布前编译项目。
render  v. 渲染  re+nder，反复生成画面  The engine can render realistic light.  这个引擎可以渲染逼真的光影。`,
};

const libraryMetaMap = {
  daily: {
    title: '日常库',
    badge: '4 列文本',
    placeholder: '请粘贴日常库文本，支持表头。字段顺序：单词 中文 日常句 句中文。\n列与列之间请至少留两个空格，或直接使用 Tab。\n缺少值可写 null。',
    helper: '示例列：单词 / 中文 / 日常句 / 句中文。导入后会同步云端，并清空本地旧缓存。',
  },
  pro: {
    title: '专业库',
    badge: '5 列文本',
    placeholder: '请粘贴专业库文本，支持表头。字段顺序：单词 词性中文 特殊记法 日常句 句中文。\n列与列之间请至少留两个空格，或直接使用 Tab。\n缺少值可写 null。',
    helper: '示例列：单词 / 词性中文 / 特殊记法 / 日常句 / 句中文。导入后会同步云端，并清空本地旧缓存。',
  },
};

Page({
  data: {
    openid: getApp().globalData.openid,
    libraryType: 'daily',
    libraryMeta: libraryMetaMap.daily,
    rawText: '',
    importing: false,
    result: null,
  },

  onShow() {
    this.setData({
      openid: getApp().globalData.openid,
    });
  },

  handleTextInput(event) {
    this.setData({
      rawText: event.detail.value,
    });
  },

  switchLibrary(event) {
    const { libraryType } = event.currentTarget.dataset;
    this.setData({
      libraryType,
      libraryMeta: libraryMetaMap[libraryType],
      result: null,
    });
  },

  fillDemoText() {
    const { libraryType } = this.data;
    this.setData({
      rawText: demoTexts[libraryType],
      result: null,
    });
  },

  clearText() {
    this.setData({
      rawText: '',
      result: null,
    });
  },

  submitImport() {
    const app = getApp();
    const { openid, libraryType, rawText, importing } = this.data;
    if (importing) {
      return;
    }
    if (!rawText.trim()) {
      wx.showToast({
        title: '请先粘贴单词文本',
        icon: 'none',
      });
      return;
    }

    this.setData({
      importing: true,
      result: null,
    });

    wx.request({
      url: `${app.globalData.apiBaseUrl}/words/import/`,
      method: 'POST',
      header: {
        'content-type': 'application/json',
      },
      data: {
        openid,
        library_type: libraryType,
        raw_text: rawText,
      },
      success: ({ data, statusCode }) => {
        if (statusCode >= 400) {
          wx.showToast({
            title: (data && data.detail) || '导入失败',
            icon: 'none',
          });
          this.setData({
            importing: false,
          });
          return;
        }

        app.clearReviewCache(libraryType);

        this.setData({
          importing: false,
          result: data,
        });

        wx.showToast({
          title: '导入完成',
          icon: 'success',
        });
      },
      fail: () => {
        this.setData({
          importing: false,
        });
        wx.showToast({
          title: '后端连接失败',
          icon: 'none',
        });
      },
    });
  },
});
