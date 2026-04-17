const featureCards = [
  {
    key: 'import',
    emoji: '📥',
    title: '导入单词',
    subtitle: '支持日常库 / 专业库，一次粘贴整批文本直接入库。',
    badge: '快速建库',
    actionText: '去导入',
  },
  {
    key: 'daily',
    emoji: '🐦',
    title: '日常模式',
    subtitle: '轻松复习日常高频词，把会话感练进脑海里。',
    badge: '轻松上手',
    actionText: '进入复习',
  },
  {
    key: 'pro',
    emoji: '🏫',
    title: '专业模式',
    subtitle: '针对专业词汇训练，强化词性辨析与记忆方法。',
    badge: '进阶训练',
    actionText: '进入复习',
  },
];

Page({
  data: {
    featureCards,
  },

  handleCardTap(event) {
    const { key } = event.currentTarget.dataset;
    if (key === 'import') {
      wx.navigateTo({
        url: '/pages/import/index',
      });
      return;
    }

    wx.navigateTo({
      url: `/pages/review/index?mode=${key}`,
    });
  },
});
