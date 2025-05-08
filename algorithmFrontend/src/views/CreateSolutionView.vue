<template>
  <div class="create-solution-view">
    <AppHeader />
    <main class="page-container">
      <h1>新建题解</h1>
      
      <el-form :model="form" label-width="120px" class="solution-form">
        <!-- 题目选择区域 -->
        <el-form-item label="题目ID">
          <div class="question-input">
            <el-input v-model="form.question_id" placeholder="输入题目ID" @blur="fetchQuestionInfo" />
            <el-button 
              type="primary" 
              icon="el-icon-link" 
              :disabled="!form.question_id" 
              @click="goToProblem"
              title="前往题目页面"
            >
              查看题目
            </el-button>
          </div>
        </el-form-item>

        <!-- 题目名称展示区域 -->
        <el-form-item label="题目名称">
          <el-input v-model="form.question_name" disabled placeholder="获取题目名称" />
        </el-form-item>

        <!-- 语言类型选择 -->
        <el-form-item label="语言类型">
          <el-input v-model="form.language" placeholder="例如: C++, Python, Java" />
        </el-form-item>

        <!-- Markdown编辑器 -->
        <el-form-item label="题解内容">
          <div class="markdown-editor">
            <el-tabs v-model="activeTab">
              <el-tab-pane label="编辑" name="edit">
                <textarea 
                  v-model="form.content" 
                  class="editor-textarea"
                  placeholder="输入题解内容（Markdown格式）"
                ></textarea>
              </el-tab-pane>
              <el-tab-pane label="预览" name="preview">
                <div class="markdown-preview" v-html="compiledMarkdown"></div>
              </el-tab-pane>
            </el-tabs>
          </div>
        </el-form-item>

        <!-- 按钮组 -->
        <el-form-item>
          <el-button type="primary" @click="publishSolutionAction" :loading="publishing">发布</el-button>
          <el-button type="info" @click="saveDraftManually" :loading="manuallySaving">保存草稿</el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </main>
  </div>
</template>

<script>
import AppHeader from '@/components/AppHeader.vue'
import { getQuestionDetail } from '@/api/question'
import { saveDraft, publishSolution } from '@/api/solution'
import MarkdownIt from 'markdown-it'
import DOMPurify from 'dompurify'

// 提前声明MathJax类型以避免no-undef错误
/* global MathJax */

export default {
  name: 'CreateSolutionView',
  components: {
    AppHeader
  },
  data() {
    return {
      activeTab: 'edit',
      fetching: false,
      publishing: false,
      manuallySaving: false,
      mdi: new MarkdownIt({
        html: true,
        linkify: true,
        typographer: true
      }),
      form: {
        question_id: '',
        question_name: '',
        language: '',
        content: ''
      },
      mathJaxLoaded: false,
      draftId: null // 保存草稿ID，用于后续更新
    }
  },
  computed: {
    compiledMarkdown() {
      try {
        const content = String(this.form.content || '')
        const html = this.mdi.render(content)
        return DOMPurify.sanitize(html)
      } catch (e) {
        console.error('Markdown处理错误:', e)
        return '内容解析出错'
      }
    }
  },
  watch: {
    activeTab(newVal) {
      if (newVal === 'preview') {
        this.initMathJax()
        this.$nextTick(() => this.renderMathJax())
      }
    },
    'form.content'() {
      if (this.activeTab === 'preview' && this.mathJaxLoaded) {
        this.$nextTick(() => this.renderMathJax())
      }
    }
  },
  mounted() {
    this.initMathJax()
  },
  methods: {
    // 新增方法：跳转到题目页面
    goToProblem() {
      if (this.form.question_id) {
        this.$router.push(`/${this.form.question_id}/problems`)
      }
    },
    
    renderMathJax() {
      if (typeof MathJax !== 'undefined' && MathJax.typesetPromise) {
        MathJax.typesetPromise()
      }
    },
    
    initMathJax() {
      if (this.mathJaxLoaded || typeof MathJax !== 'undefined') {
        this.mathJaxLoaded = true
        return
      }

      // 配置MathJax
      window.MathJax = {
        tex: {
          inlineMath: [['$', '$'], ['\\(', '\\)']],
          displayMath: [['$$', '$$'], ['\\[', '\\]']],
          processEscapes: true
        },
        options: {
          skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code']
        },
        startup: {
          ready: () => {
            MathJax.startup.defaultReady()
            this.mathJaxLoaded = true
            if (this.activeTab === 'preview') {
              this.$nextTick(() => this.renderMathJax())
            }
          }
        }
      }

      // 加载MathJax脚本
      const script = document.createElement('script')
      script.src = 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js'
      script.async = true
      script.onload = () => {
        this.mathJaxLoaded = true
      }
      document.head.appendChild(script)
    },
    async fetchQuestionInfo() {
      if (!this.form.question_id) {
        this.form.question_name = ''
        return
      }

      this.fetching = true
      try {
        const response = await getQuestionDetail(this.form.question_id)
        this.form.question_name = response.data.name
      } catch (error) {
        console.error('获取题目信息失败:', error)
        this.$message.error('获取题目信息失败: ' + (error.message || '未知错误'))
        this.form.question_name = ''
      } finally {
        this.fetching = false
      }
    },
    
    // 手动保存草稿
    async saveDraftManually() {
      if (!this.validateForm(true)) return
      
      this.manuallySaving = true
      
      try {
        // 构建请求数据，使用正确的字段名
        const requestData = {
          question_id: this.form.question_id,
          language: this.form.language,
          content: this.form.content
        }
        
        // 打印请求数据，用于调试
        console.log('发送草稿保存请求:', requestData)
        
        const response = await saveDraft(requestData)
        
        console.log('草稿保存响应:', response.data)
        
        if (response.data && response.data.code === 200) {
          this.draftId = response.data.data.id
          this.$message.success('草稿保存成功')
        } else {
          this.$message.error((response.data && response.data.message) || '保存失败')
        }
      } catch (error) {
        console.error('保存草稿失败:', error)
        
        // 尝试提取响应中的错误信息
        if (error.response && error.response.data) {
          console.log('错误响应详情:', error.response.data)
          this.$message.error(error.response.data.message || '保存失败')
        } else {
          this.$message.error(error.message || '保存失败')
        }
      } finally {
        this.manuallySaving = false
      }
    },
    
    // 发布题解（正式版本）
    async publishSolutionAction() {
      if (!this.validateForm()) return
      
      this.publishing = true
      try {
        const requestData = {
          question_id: this.form.question_id,
          language: this.form.language,
          content: this.form.content
        }
        
        // 打印请求数据，用于调试
        console.log('发布题解请求:', requestData)
        
        const response = await publishSolution(requestData)
        
        console.log('发布题解响应:', response.data)
        
        if (response.data && response.data.code === 200) {
          this.$message.success('题解发布成功')
          // 发布成功后可以跳转到题解列表或详情页
          // this.$router.push('/solutions')
        } else {
          this.$message.error((response.data && response.data.message) || '发布失败')
        }
      } catch (error) {
        console.error('发布题解失败:', error)
        
        // 尝试提取响应中的错误信息
        if (error.response && error.response.data) {
          console.log('错误响应详情:', error.response.data)
          this.$message.error(error.response.data.message || '发布失败')
        } else {
          this.$message.error(error.message || '发布失败')
        }
      } finally {
        this.publishing = false
      }
    },
    
    validateForm(isDraft = false) {
      if (!this.form.question_id) {
        this.$message.error('请输入题目ID')
        return false
      }
      if (!this.form.question_name && !isDraft) {
        this.$message.error('题目ID无效或未获取到题目名称')
        return false
      }
      if (!this.form.language) {
        this.$message.error('请输入语言类型')
        return false
      }
      if (!this.form.content) {
        this.$message.error('请输入题解内容')
        return false
      }
      return true
    },
    
    resetForm() {
      this.form = {
        question_id: '',
        question_name: '',
        language: '',
        content: ''
      }
      this.draftId = null
    }
  }
}
</script>

<style scoped>
.create-solution-view {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%);
  padding-top: 60px;
}

.page-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 30px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  backdrop-filter: blur(5px);
  border: 1px solid rgba(0, 0, 0, 0.03);
}

.page-container h1 {
  font-size: 2rem;
  color: #2c3e50;
  margin-bottom: 2rem;
  font-weight: 600;
  text-align: center;
  text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
}

.solution-form {
  max-width: 800px;
  margin: 0 auto;
}

.question-input {
  display: flex;
  gap: 12px;
}

.question-input .el-input {
  flex: 1;
  border-radius: 8px;
  overflow: hidden;
}

.el-form-item {
  margin-bottom: 22px;
}

.el-form-item:last-child {
  margin-bottom: 0;
}

.markdown-editor {
  width: 100%;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

:deep(.markdown-editor .el-tabs__header) {
  margin: 0;
}

:deep(.markdown-editor .el-tabs__nav-wrap) {
  padding: 0 15px;
  background: #f8f9fa;  
}

:deep(.markdown-editor .el-tabs__item) {
  padding: 0 20px;
  height: 40px;
  line-height: 40px;
}

.editor-textarea {
  width: 100%;
  min-height: 400px;
  padding: 15px;
  border: none;
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
  font-size: 14px;
  line-height: 1.6;
  resize: vertical;
  background: #fff;
  color: #333;
}

.markdown-preview {
  padding: 20px;
  min-height: 400px;
  background: #fff;
  overflow: auto;
}

/* MathJax公式样式 */
.markdown-preview :deep(.MathJax) {
  color: #333;
}

/* 其他Markdown样式 */
.markdown-preview :deep(h1),
.markdown-preview :deep(h2),
.markdown-preview :deep(h3) {
  margin-top: 1em;
  margin-bottom: 0.5em;
  color: #333;
}

.markdown-preview :deep(pre) {
  background-color: #f6f8fa;
  padding: 12px;
  border-radius: 6px;
  overflow: auto;
}

.markdown-preview :deep(code) {
  background-color: #f6f8fa;
  padding: 0.2em 0.4em;
  border-radius: 3px;
  font-family: monospace;
  color: #c7254e;
}

.markdown-preview :deep(blockquote) {
  border-left: 4px solid #dfe2e5;
  color: #6a737d;
  padding: 0 1em;
  margin-left: 0;
}

.markdown-preview :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 1em 0;
}

.markdown-preview :deep(th),
.markdown-preview :deep(td) {
  border: 1px solid #dfe2e5;
  padding: 0.6em 1em;
}

.markdown-preview :deep(ul),
.markdown-preview :deep(ol) {
  padding-left: 2em;
  margin: 1em 0;
}

.markdown-preview :deep(li) {
  margin: 0.5em 0;
}

.markdown-preview :deep(a) {
  color: #409eff;
  text-decoration: none;
}

.markdown-preview :deep(a:hover) {
  text-decoration: underline;
}

.markdown-preview :deep(img) {
  max-width: 100%;
  border-radius: 4px;
}

/* 按钮组样式 */
.el-form-item:last-child {
  margin-top: 30px;
  text-align: center;
}

.el-form-item:last-child .el-button {
  min-width: 120px;
  height: 40px;
  margin: 0 8px;
}

/* 禁用输入框样式 */
:deep(.el-input.is-disabled .el-input__inner) {
  background-color: #f8f9fa;
  color: #606266;
  border-color: #e4e7ed;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .page-container {
    padding: 20px;
    border-radius: 0;
  }
  
  .question-input {
    flex-direction: column;
  }
  
  .editor-textarea,
  .markdown-preview {
    min-height: 300px;
  }
  
  .el-form-item:last-child .el-button {
    width: 100%;
    margin: 8px 0;
  }
}
</style>