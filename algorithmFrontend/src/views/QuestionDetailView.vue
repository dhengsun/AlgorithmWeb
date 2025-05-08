<template>
  <div class="question-detail-view">
    <AppHeader />
    <main class="page-container">
      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="10" animated />
      </div>
      
      <div v-else-if="error" class="error-container">
        <el-alert
          :title="error"
          type="error"
          :closable="false"
        />
      </div>
      
      <div v-else class="question-content">
        <div class="left-section">
          <el-card class="question-description-card">
            <!-- 根据平台选择不同的渲染方式 -->
            <div v-if="question.oj_platform === 'leetcode'" v-html="compiledHtml" class="html-content"></div>
            <div v-else v-html="compiledMarkdown" class="markdown-content"></div>
          </el-card>
        </div>
        
        <div class="right-section">
          <el-card class="question-info-card">
            <h2>{{ question.name }}</h2>
            <div class="info-meta">
              <div>题目ID: {{ question.id }}</div>
              <div>外部ID: {{ question.ext_question_id }}</div>
              <div>
                平台: 
                <el-tag :type="getPlatformTagType(question.oj_platform)" size="small">
                  {{ getPlatformName(question.oj_platform) }}
                </el-tag>
              </div>
              <div>创建时间: {{ formatDate(question.created_at) }}</div>
              <div v-if="question.is_deleted" class="deleted-status">
                <el-tag type="danger" effect="dark">已删除</el-tag>
              </div>
            </div>
            
            <div class="action-buttons">
              <el-button type="primary" size="small" @click="handleEdit" :disabled="question.is_deleted">
                <el-icon><EditPen /></el-icon>
                编辑
              </el-button>
              
              <!-- 根据is_deleted显示不同的按钮 -->
              <el-button 
                v-if="!question.is_deleted" 
                type="danger" 
                size="small" 
                @click="handleDelete"
              >
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
              
              <el-button 
                v-else 
                type="success" 
                size="small" 
                @click="handleRestore"
              >
                <el-icon><RefreshRight /></el-icon>
                恢复
              </el-button>
              
              <el-button 
                type="success" 
                size="small" 
                @click="handleCreateSolution" 
                :disabled="question.is_deleted"
              >
                <el-icon><Plus /></el-icon>
                创建题解
              </el-button>
            </div>
          </el-card>
          
          <el-card class="question-tags-card">
            <div class="difficulty-section">
              <h3>难度级别</h3>
              <el-tag 
                :type="getDifficultyTagType(question)"
                effect="dark"
              >
                {{ question.difficulty }}
              </el-tag>
            </div>
            
            <div class="tags-section">
              <h3>算法标签</h3>
              <div class="tags-container">
                <el-tag 
                  v-for="tag in question.algorithm_tags" 
                  :key="tag"
                  :type="getTagType(tag, question.oj_platform)"
                  class="algorithm-tag"
                >
                  {{ getTagName(tag) }}
                </el-tag>
              </div>
            </div>
          </el-card>
          
          <!-- 可以添加更多卡片，如相关题目等 -->
          <el-card class="related-questions-card" v-if="false">
            <h3>相关题目</h3>
            <div class="related-questions-list">
              <!-- 相关题目列表，暂不实现 -->
            </div>
          </el-card>
        </div>
      </div>
    </main>

    <!-- 删除确认对话框 -->
    <el-dialog
      v-model="deleteDialogVisible"
      title="确认删除"
      width="30%"
    >
      <span>确定要删除题目 "{{ question ? question.name : '' }}" 吗？此操作不可逆。</span>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="deleteDialogVisible = false">取消</el-button>
          <el-button type="danger" @click="confirmDelete" :loading="processing">确认删除</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 恢复确认对话框 -->
    <el-dialog
      v-model="restoreDialogVisible"
      title="确认恢复"
      width="30%"
    >
      <span>确定要恢复题目 "{{ question ? question.name : '' }}" 吗？</span>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="restoreDialogVisible = false">取消</el-button>
          <el-button type="success" @click="confirmRestore" :loading="processing">确认恢复</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import AppHeader from '@/components/AppHeader.vue'
import { getQuestionDetail, deleteQuestion, restoreQuestion } from '@/api/question'
import MarkdownIt from 'markdown-it'
import DOMPurify from 'dompurify'
import { EditPen, Delete, Plus, RefreshRight } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

/* global MathJax */

export default {
  name: 'QuestionDetailView',
  components: {
    AppHeader,
    EditPen,
    Delete,
    Plus,
    RefreshRight
  },
  data() {
    return {
      questionId: this.$route.params.id,
      question: null,
      loading: true,
      error: null,
      mdi: new MarkdownIt({
        html: true,
        linkify: true,
        typographer: true
      }),
      mathJaxLoaded: false,
      
      // 删除和恢复相关状态
      deleteDialogVisible: false,
      restoreDialogVisible: false,
      processing: false
    }
  },
  computed: {
    // 用于洛谷等平台 - Markdown 渲染
    compiledMarkdown() {
      if (!this.question || !this.question.content) return ''
      
      try {
        const content = String(this.question.content || '')
        const html = this.mdi.render(content)
        return DOMPurify.sanitize(html)
      } catch (e) {
        console.error('Markdown处理错误:', e)
        return '内容解析出错'
      }
    },
    
    // 用于LeetCode平台 - HTML直接渲染
    compiledHtml() {
      if (!this.question || !this.question.content) return ''
      
      try {
        let content = String(this.question.content || '')
        
        // 检查是否需要HTML包装
        if (!content.trim().startsWith('<')) {
          // 如果内容不是以HTML标签开始，则添加基本HTML包装
          content = `<div>${content}</div>`
        }
        
        // 处理LeetCode特有的代码块格式
        content = this.processLeetcodeHtml(content)
        
        // 添加示例块样式处理
        content = this.wrapExamples(content)
        
        // 清洗HTML以确保安全
        return DOMPurify.sanitize(content, {
          USE_PROFILES: { html: true },
          ALLOWED_TAGS: [
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'br', 'hr',
            'ol', 'ul', 'li', 'pre', 'code', 'blockquote',
            'table', 'thead', 'tbody', 'tr', 'th', 'td',
            'strong', 'em', 'b', 'i', 'u', 'strike', 's',
            'a', 'img', 'span', 'div', 'section', 'article',
            'meta'
          ],
          ALLOWED_ATTR: [
            'href', 'name', 'target', 'src', 'alt', 'class', 'id',
            'width', 'height', 'style', 'charset', 'content'
          ]
        })
      } catch (e) {
        console.error('HTML处理错误:', e)
        return '内容解析出错'
      }
    }
  },
  watch: {
    // 当内容变化时更新MathJax渲染
    question: {
      handler() {
        this.$nextTick(() => this.renderMathJax())
      },
      deep: true
    }
  },
  mounted() {
    this.fetchQuestionDetail()
    this.initMathJax()
  },
  methods: {
    // 编辑按钮处理
    handleEdit() {
      if (!this.question || this.question.is_deleted) return
      // 跳转到更新题目页面
      this.$router.push(`/questions/update/${this.question.id}`)
    },
    
    // 删除按钮处理
    handleDelete() {
      if (!this.question || this.question.is_deleted) return
      this.deleteDialogVisible = true
    },
    
    // 恢复按钮处理
    handleRestore() {
      if (!this.question || !this.question.is_deleted) return
      this.restoreDialogVisible = true
    },
    
    // 确认删除
    async confirmDelete() {
      if (!this.question) return
      
      this.processing = true
      try {
        await deleteQuestion({ id: this.question.id })
        
        ElMessage({
          type: 'success',
          message: '题目删除成功'
        })
        
        // 关闭对话框
        this.deleteDialogVisible = false
        
        // 刷新数据
        this.fetchQuestionDetail()
      } catch (error) {
        console.error('删除题目失败:', error)
        ElMessage({
          type: 'error',
          message: '删除题目失败: ' + (error.message || '未知错误')
        })
      } finally {
        this.processing = false
      }
    },
    
    // 确认恢复
    async confirmRestore() {
      if (!this.question) return
      
      this.processing = true
      try {
        await restoreQuestion({ id: this.question.id })
        
        ElMessage({
          type: 'success',
          message: '题目恢复成功'
        })
        
        // 关闭对话框
        this.restoreDialogVisible = false
        
        // 刷新数据
        this.fetchQuestionDetail()
      } catch (error) {
        console.error('恢复题目失败:', error)
        ElMessage({
          type: 'error',
          message: '恢复题目失败: ' + (error.message || '未知错误')
        })
      } finally {
        this.processing = false
      }
    },
    
    // 创建题解按钮处理
    handleCreateSolution() {
      if (!this.question || this.question.is_deleted) return
      // 跳转到创建题解页面，传递题目ID
      this.$router.push(`/create/solution?question_id=${this.question.id}`)
    },
    
    // 处理LeetCode HTML内容
    processLeetcodeHtml(content) {
      try {
        // 检查内容类型
        if (content.includes('\\n') || content.includes('&lt;') || content.includes('&gt;')) {
          // 这是LeetCode转义后的文本，需要先转换
          content = this.convertLeetcodeEscapedContent(content)
        }
        
        // 创建临时DOM元素来处理HTML
        const tempDiv = document.createElement('div')
        tempDiv.innerHTML = content
        
        // 确保所有代码块都有正确的样式
        const preTags = tempDiv.querySelectorAll('pre')
        preTags.forEach(preTag => {
          // 添加类名以确保正确样式
          preTag.classList.add('leetcode-code-block')
          
          // 处理内部的code标签
          const codeTag = preTag.querySelector('code')
          if (codeTag) {
            // 如果没有语言类，添加一个默认类
            if (!codeTag.className.includes('language-')) {
              codeTag.classList.add('language-plain')
            }
          }
        })
        
        // 确保在表格外添加包装以提高可滚动性
        const tables = tempDiv.querySelectorAll('table')
        tables.forEach(table => {
          const wrapper = document.createElement('div')
          wrapper.className = 'table-responsive'
          table.parentNode.insertBefore(wrapper, table)
          wrapper.appendChild(table)
        })
        
        // 处理示例中的加粗内容
        const boldPatterns = tempDiv.querySelectorAll('*:not(strong):not(b)')
        boldPatterns.forEach(el => {
          const text = el.innerHTML
          if (text && typeof text === 'string') {
            // 查找并替换 **文本** 格式为 <strong>文本</strong>
            if (text.includes('**')) {
              el.innerHTML = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            }
          }
        })
        
        // 为LeetCode内容添加meta标签，指示渲染模式
        const metaTag = document.createElement('meta')
        metaTag.setAttribute('name', 'rendering-mode')
        metaTag.setAttribute('content', 'leetcode-html')
        tempDiv.insertBefore(metaTag, tempDiv.firstChild)
        
        return tempDiv.innerHTML
      } catch (error) {
        console.error('处理LeetCode HTML时出错:', error)
        return content // 出错时返回原始内容
      }
    },
    
    // 转换LeetCode转义的内容为格式化HTML
    convertLeetcodeEscapedContent(content) {
      // 处理转义字符
      content = content
        .replace(/&lt;/g, '<')
        .replace(/&gt;/g, '>')
        .replace(/&nbsp;/g, ' ')
        .replace(/&amp;/g, '&')
        .replace(/&quot;/g, '"')
        .replace(/&#39;/g, "'")
      
      // 处理换行符 \n 转为实际的HTML换行
      content = content.replace(/\\n/g, '<br>')
      
      // 处理制表符
      content = content.replace(/\\t/g, '&emsp;&emsp;')
      
      // 如果有空行，添加段落标签以保持间距
      content = content
        .replace(/(<br>){2,}/g, '</p><p>')  // 多个连续换行符转为段落
        .replace(/<br>/g, '<br>\n')  // 单个换行符后添加实际换行符以改善源码可读性
      
      // 处理示例部分的格式
      content = content
        .replace(/示例 (\d+):/g, '<h3>示例 $1</h3>')
        .replace(/输入: /g, '<strong>输入</strong>: ')
        .replace(/输出: /g, '<strong>输出</strong>: ')
        .replace(/解释: /g, '<strong>解释</strong>: ')
      
      // 处理提示/注意部分
      content = content.replace(/提示:|注意:/g, '<h3>$&</h3>')
      
      // 确保内容被包裹在段落标签中
      if (!content.startsWith('<') || !['<p', '<div', '<h'].includes(content.substring(0, 2))) {
        content = '<p>' + content + '</p>'
      }
      
      return content
    },
    
    // 包装示例部分为特殊的样式块
    wrapExamples(content) {
      try {
        const tempDiv = document.createElement('div')
        tempDiv.innerHTML = content
        
        // 查找所有示例标题
        const exampleHeadings = tempDiv.querySelectorAll('h3')
        exampleHeadings.forEach(heading => {
          if (heading.textContent.includes('示例')) {
            // 找到包含此示例的所有内容
            let exampleContent = []
            let currentNode = heading.nextElementSibling
            
            // 收集直到下一个标题或某个终止条件的所有内容
            while (currentNode && 
                  (currentNode.tagName !== 'H3' && 
                   !currentNode.textContent.includes('提示') && 
                   !currentNode.textContent.includes('注意'))) {
              exampleContent.push(currentNode.cloneNode(true))
              currentNode = currentNode.nextElementSibling
            }
            
            // 创建示例块容器
            const exampleBlock = document.createElement('div')
            exampleBlock.className = 'example-block'
            
            // 添加标题和内容
            exampleBlock.appendChild(heading.cloneNode(true))
            exampleContent.forEach(node => {
              exampleBlock.appendChild(node)
            })
            
            // 替换原始内容
            heading.parentNode.insertBefore(exampleBlock, heading)
            
            // 移除原始元素
            heading.remove()
            exampleContent.forEach(node => {
              const originalNode = tempDiv.querySelector(`*:nth-child(${Array.from(tempDiv.children).indexOf(node) + 1})`)
              if (originalNode) {
                originalNode.remove()
              }
            })
          }
        })
        
        return tempDiv.innerHTML
      } catch (error) {
        console.error('包装示例部分时出错:', error)
        return content // 出错时返回原始内容
      }
    },
    
    renderMathJax() {
      if (typeof MathJax !== 'undefined' && MathJax.typesetPromise && this.mathJaxLoaded) {
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
            this.$nextTick(() => this.renderMathJax())
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
    
    async fetchQuestionDetail() {
      this.loading = true
      this.error = null
      
      try {
        const response = await getQuestionDetail(this.questionId)
        this.question = response.data
        
        // 确保算法标签是数组
        if (typeof this.question.algorithm_tags === 'string') {
          this.question.algorithm_tags = this.question.algorithm_tags
            .split(',')
            .map(tag => tag.trim())
            .filter(tag => tag.length > 0)
        }
      } catch (error) {
        console.error('获取题目详情失败:', error)
        this.error = '获取题目详情失败: ' + (error.message || '未知错误')
      } finally {
        this.loading = false
      }
    },
    
    // 平台相关方法
    getPlatformName(platform) {
      const platforms = {
        'luogu': '洛谷',
        'leetcode': 'LeetCode',
        // 可以添加更多平台
      }
      return platforms[platform] || platform
    },
    
    // 平台标签样式
    getPlatformTagType(platform) {
      return {
        luogu: 'success',
        leetcode: 'warning'
      }[platform] || 'info'
    },
    
    // 日期格式化
    formatDate(dateString) {
      if (!dateString) return ''
      
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    },
    
    // 难度标签样式
    getDifficultyTagType(row) {
      if (row.oj_platform === 'luogu') {
        const levelMap = {
          '入门': 'info',
          '普及-': 'success',
          '普及/提高-': 'success',
          '普及+/提高': 'warning',
          '提高+/省选-': 'danger',
          '省选/NOI-': 'danger',
          'NOI/NOI+': 'danger',
          'CTSC': 'danger'
        }
        return levelMap[row.difficulty] || 'info'
      }
      
      // LeetCode难度
      return {
        '简单': 'success',
        '中等': 'warning',
        '困难': 'danger'
      }[row.difficulty] || 'info'
    },
    
    // 标签样式
    getTagType(tag, platform) {
      // LeetCode标签统一为蓝色
      if (platform === 'leetcode') return 'primary'
      
      // 洛谷标签根据前缀分类
      const prefix = tag.split('_')[0]
      return {
        'Algorithm': 'primary',  // 算法 - 蓝色
        'Source': 'success',     // 来源 - 绿色
        'Time': 'warning',       // 时间 - 黄色
        'Region': 'danger',      // 地区 - 红色
        'Other': 'info'          // 其他 - 灰色
      }[prefix] || 'info'
    },
    
    // 获取标签名称
    getTagName(tag) {
      // 洛谷标签去掉前缀
      const parts = tag.split('_')
      if (parts.length > 1) {
        return parts.slice(1).join('_')
      }
      return tag
    },
    
    // 生成题目链接
    generateOjLink(row) {
      const baseUrls = {
        luogu: `https://www.luogu.com.cn/problem/${row.ext_question_id}`,
        leetcode: `https://leetcode.cn/problems/${row.ext_question_id}/`
      }
      return baseUrls[row.oj_platform] || '#'
    }
  }
}
</script>

<style scoped>
/* 基础布局优化 */
.question-detail-view {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
}

.page-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
}

/* 加载状态优化 */
.loading-container {
  padding: 3rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

/* 错误状态优化 */
.error-container {
  padding: 2rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

/* 主内容区网格布局 */
.question-content {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 340px;
  gap: 2rem;
  align-items: start;
}

/* 左侧题目内容区 */
.left-section {
  position: sticky;
  top: 1rem;
}

/* 右侧信息卡片区 */
.right-section {
  display: grid;
  gap: 1.5rem;
  position: sticky;
  top: 1rem;
  align-self: start;
}

/* 卡片通用样式 */
.el-card {
  border-radius: 12px;
  border: none;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  margin-bottom: 1.5rem;
}

.el-card:hover {
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

/* 题目描述卡片 */
.question-description-card {
  padding: 2rem;
  background: white;
}

/* 题目信息卡片 */
.question-info-card {
  padding: 1.5rem;
}

.question-info-card h2 {
  font-size: 1.4rem;
  color: #2d3748;
  margin-bottom: 1rem;
  font-weight: 600;
  line-height: 1.3;
}

.info-meta {
  display: grid;
  gap: 0.8rem;
  color: #4a5568;
  font-size: 0.95rem;
  margin: 1.5rem 0;
}

.info-meta div {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/* 标签卡片 */
.question-tags-card {
  padding: 1.5rem;
}

.difficulty-section,
.tags-section {
  margin-bottom: 1.5rem;
}

.difficulty-section h3,
.tags-section h3 {
  font-size: 1.1rem;
  color: #2d3748;
  margin-bottom: 0.8rem;
  font-weight: 500;
}

/* 操作按钮组 */
.action-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 0.8rem;
  margin-top: 1.5rem;
}

.action-buttons .el-button {
  flex: 1 0 auto;
  min-width: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  transition: all 0.3s ease;
}

/* 标签容器 */
.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
}

.algorithm-tag {
  transition: all 0.3s ease;
  margin: 0;
}

.algorithm-tag:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

/* 内容渲染样式优化 */
.markdown-content,
.html-content {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  color: #2d3748;
  line-height: 1.7;
  font-size: 1rem;
}

/* 标题样式 */
.markdown-content :deep(h1),
.markdown-content :deep(h2),
.markdown-content :deep(h3),
.html-content :deep(h1),
.html-content :deep(h2),
.html-content :deep(h3) {
  color: #1a202c;
  font-weight: 600;
  margin: 1.8rem 0 1rem;
  scroll-margin-top: 80px; /* 为锚点跳转留出空间 */
}

.markdown-content :deep(h1),
.html-content :deep(h1) {
  font-size: 1.8rem;
  border-bottom: 1px solid #e2e8f0;
  padding-bottom: 0.5rem;
}

.markdown-content :deep(h2),
.html-content :deep(h2) {
  font-size: 1.5rem;
}

.markdown-content :deep(h3),
.html-content :deep(h3) {
  font-size: 1.2rem;
}

/* 段落样式 */
.markdown-content :deep(p),
.html-content :deep(p) {
  margin: 1.2rem 0;
  color: #4a5568;
}

/* 代码块样式 */
.markdown-content :deep(pre),
.html-content :deep(pre) {
  background: #1e293b;
  border-radius: 8px;
  padding: 1.2rem;
  margin: 1.5rem 0;
  overflow-x: auto;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.markdown-content :deep(code),
.html-content :deep(code) {
  font-family: 'Fira Code', 'SFMono-Regular', Consolas, monospace;
  background: transparent;
  color: #f8fafc;
  padding: 0;
  font-size: 0.9em;
}

/* 行内代码 */
.markdown-content :deep(p > code),
.html-content :deep(p > code) {
  background: #edf2f7;
  color: #c53030;
  padding: 0.2em 0.4em;
  border-radius: 4px;
  font-size: 0.9em;
}

/* 引用块 */
.markdown-content :deep(blockquote),
.html-content :deep(blockquote) {
  border-left: 4px solid #4299e1;
  background: #ebf8ff;
  color: #2b6cb0;
  padding: 1rem 1.5rem;
  margin: 1.5rem 0;
  border-radius: 0 4px 4px 0;
}

/* 表格样式 */
.markdown-content :deep(table),
.html-content :deep(table) {
  width: 100%;
  margin: 1.5rem 0;
  border-collapse: collapse;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.markdown-content :deep(th),
.markdown-content :deep(td),
.html-content :deep(th),
.html-content :deep(td) {
  border: 1px solid #e2e8f0;
  padding: 0.75rem 1rem;
  text-align: left;
}

.markdown-content :deep(th),
.html-content :deep(th) {
  background: #f7fafc;
  font-weight: 600;
  color: #2d3748;
}

/* 列表样式 */
.markdown-content :deep(ul),
.markdown-content :deep(ol),
.html-content :deep(ul),
.html-content :deep(ol) {
  margin: 1.5rem 0;
  padding-left: 2rem;
}

.markdown-content :deep(li),
.html-content :deep(li) {
  margin: 0.5rem 0;
  color: #4a5568;
}

/* 链接样式 */
.markdown-content :deep(a),
.html-content :deep(a) {
  color: #4299e1;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.2s;
}

.markdown-content :deep(a:hover),
.html-content :deep(a:hover) {
  color: #2b6cb0;
  text-decoration: underline;
}

/* 图片样式 */
.markdown-content :deep(img),
.html-content :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 6px;
  margin: 1.5rem auto;
  display: block;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* LeetCode 特定样式 */
.html-content :deep(.example-block) {
  background: #f0f9ff;
  border-left: 3px solid #63b3ed;
  padding: 1.2rem;
  margin: 1.8rem 0;
  border-radius: 0 6px 6px 0;
}

.html-content :deep(.example-block h3) {
  margin-top: 0;
  color: #2c5282;
}

.html-content :deep(.table-responsive) {
  overflow-x: auto;
  margin: 1.8rem 0;
  border-radius: 6px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

/* 对话框样式优化 */
.el-dialog {
  border-radius: 12px;
  max-width: 500px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.8rem;
  margin-top: 1.5rem;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .question-content {
    grid-template-columns: 1fr;
  }
  
  .right-section {
    position: static;
  }
}

@media (max-width: 768px) {
  .page-container {
    padding: 1rem;
  }
  
  .action-buttons {
    /* 保持水平排列 */
    display: flex;
    flex-wrap: wrap;
  }
  
  .question-description-card,
  .question-info-card,
  .question-tags-card {
    padding: 1.2rem;
  }
}

@media (max-width: 480px) {
  .action-buttons {
    flex-direction: column;
  }
  
  .action-buttons .el-button {
    width: 100%;
  }
}

/* 动画效果 */
.el-card,
.el-button,
.el-tag {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f5f9;
}

::-webkit-scrollbar-thumb {
  background: #cbd5e0;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a0aec0;
}
</style>