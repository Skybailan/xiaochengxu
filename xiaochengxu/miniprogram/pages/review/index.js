const modeMetaMap = {
  daily: {
    title: '日常模式',
    badge: '轻松复习',
    endpoint: '/review/daily/',
  },
  pro: {
    title: '专业模式',
    badge: '专业训练',
    endpoint: '/review/pro/',
  },
};

Page({
  data: {
    mode: 'daily',
    modeMeta: modeMetaMap.daily,
    loading: true,
    loadError: '',
    questions: [],
    currentIndex: 0,
    currentQuestion: null,
    total: 0,
    progressText: '0/0',
    progressPercent: 0,
    selectedOptionId: null,
    submitted: false,
    selectedCorrect: false,
    hintStep: 0,
    hintVisible: false,
    showMemoryMethod: false,
    hintButtonText: '提示',
    submitButtonText: '提交',
    submitButtonClass: 'disabled-button',
    submitDisabled: true,
    showCompleteModal: false,
    dataSourceText: '',
  },

  onLoad(options) {
    const mode = options.mode === 'pro' ? 'pro' : 'daily';

    this.audioContext = wx.createInnerAudioContext();
    this.audioContext.autoplay = true;
    this.setData({
      mode,
      modeMeta: modeMetaMap[mode],
      hintButtonText: '提示',
    });
    this.fetchQuestions();
  },

  onUnload() {
    if (this.audioContext) {
      this.audioContext.destroy();
    }
  },

  fetchQuestions() {
    const app = getApp();
    const { mode } = this.data;
    const { endpoint } = modeMetaMap[mode];
    const cachedPayload = app.getReviewCache(mode);

    this.setData({
      loading: true,
      loadError: '',
      showCompleteModal: false,
    });

    wx.request({
      url: `${app.globalData.apiBaseUrl}${endpoint}`,
      method: 'GET',
      data: {
        openid: app.globalData.openid,
      },
      success: ({ data, statusCode }) => {
        if (statusCode >= 400) {
          if (cachedPayload) {
            this.applyQuestionPayload(cachedPayload, false);
            return;
          }

          const message = data && data.detail ? data.detail : '服务暂时不可用';
          this.setData({
            loading: false,
            loadError: message,
          });
          return;
        }

        app.setReviewCache(mode, data);
        this.applyQuestionPayload(data, true);
      },
      fail: () => {
        if (cachedPayload) {
          this.applyQuestionPayload(cachedPayload, false);
          return;
        }

        this.setData({
          loading: false,
          loadError: '无法连接后端服务，请检查 Django 服务地址是否可访问。',
        });
      },
    });
  },

  applyQuestionPayload(payload, fromRemote) {
    const questions = (payload && payload.items) || [];
    this.setData(
      {
        questions,
        total: questions.length,
        loading: false,
        currentIndex: 0,
        loadError: '',
        dataSourceText: fromRemote ? '云端同步成功' : '当前为本地缓存内容',
      },
      () => {
        this.loadCurrentQuestion();
      }
    );
  },

  loadCurrentQuestion() {
    const { questions, currentIndex, total } = this.data;
    if (!questions.length || currentIndex >= total) {
      this.setData({
        currentQuestion: null,
        progressText: `${total}/${total}`,
        progressPercent: total ? 100 : 0,
        showCompleteModal: total > 0,
      });
      return;
    }

    const currentQuestion = questions[currentIndex];
    this.setData(
      {
        currentQuestion,
        progressText: `${currentIndex}/${total}`,
        progressPercent: total ? Math.round((currentIndex / total) * 100) : 0,
        selectedOptionId: null,
        submitted: false,
        selectedCorrect: false,
        hintStep: 0,
        hintVisible: false,
        showMemoryMethod: false,
        hintButtonText: '提示',
        submitButtonText: '提交',
        submitButtonClass: 'disabled-button',
        submitDisabled: true,
      },
      () => {
        this.playPronunciation();
      }
    );
  },

  getHintButtonText(step) {
    const { mode } = this.data;
    if (mode === 'daily') {
      return step > 0 ? '已展开提示' : '提示';
    }
    if (step === 0) {
      return '提示';
    }
    if (step === 1) {
      return '再看记忆法';
    }
    return '提示已全部展开';
  },

  updateHintState(step, extra = {}) {
    this.setData({
      hintStep: step,
      hintButtonText: this.getHintButtonText(step),
      ...extra,
    });
  },

  toggleHint() {
    const { mode, hintStep, submitted } = this.data;
    if (submitted) {
      this.updateHintState(mode === 'pro' ? 2 : 1, {
        hintVisible: true,
        showMemoryMethod: mode === 'pro',
      });
      return;
    }

    if (mode === 'daily') {
      this.updateHintState(1, {
        hintVisible: true,
      });
      return;
    }

    if (hintStep === 0) {
      this.updateHintState(1, {
        hintVisible: true,
        showMemoryMethod: false,
      });
      return;
    }

    this.updateHintState(2, {
      hintVisible: true,
      showMemoryMethod: true,
    });
  },

  selectOption(event) {
    const { submitted } = this.data;
    if (submitted) {
      return;
    }

    const optionId = event.currentTarget.dataset.optionId;
    this.setData({
      selectedOptionId: optionId,
      submitButtonText: '提交',
      submitButtonClass: 'secondary-button',
      submitDisabled: false,
    });
  },

  handleSubmitOrContinue() {
    const { submitted, selectedOptionId, currentQuestion, currentIndex, mode, total } = this.data;
    if (!currentQuestion) {
      return;
    }

    if (submitted) {
      const nextIndex = currentIndex + 1;
      this.setData(
        {
          currentIndex: nextIndex,
        },
        () => {
          this.loadCurrentQuestion();
        }
      );
      return;
    }

    if (!selectedOptionId) {
      return;
    }

    const selectedOption = currentQuestion.options.find((item) => item.word_id === selectedOptionId);
    const selectedCorrect = !!(selectedOption && selectedOption.is_correct);

    this.setData({
      submitted: true,
      selectedCorrect,
      hintVisible: true,
      hintStep: mode === 'pro' ? 2 : 1,
      showMemoryMethod: mode === 'pro',
      hintButtonText: this.getHintButtonText(mode === 'pro' ? 2 : 1),
      submitButtonText: '继续',
      submitButtonClass: selectedCorrect ? 'primary-button' : 'danger-button',
      submitDisabled: false,
      progressText: `${currentIndex + 1}/${total}`,
      progressPercent: total ? Math.round(((currentIndex + 1) / total) * 100) : 0,
    });
  },

  playPronunciation() {
    const { currentQuestion } = this.data;
    if (!currentQuestion || !currentQuestion.word || !this.audioContext) {
      return;
    }
    this.audioContext.stop();
    this.audioContext.src = `https://dict.youdao.com/dictvoice?type=0&audio=${encodeURIComponent(currentQuestion.word)}`;
    this.audioContext.play();
  },

  goHome() {
    wx.reLaunch({
      url: '/pages/index/index',
    });
  },
});
