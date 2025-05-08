<template>
  <div class="create-view">
    <AppHeader />
    <div class="layout-container">
      <!-- 左侧操作面板 -->
      <div class="control-panel">
        <h1>新建题目</h1>
        
        <el-form :model="form" label-width="100px" class="problem-form">
          <!-- URL输入和抓取按钮 -->
          <el-form-item label="题目URL">
            <div class="url-input">
              <el-input v-model="form.url" placeholder="输入题目URL" />
              <el-button 
                type="primary" 
                @click="fetchQuestionInfo"
                :loading="fetching"
              >
                提取题目信息
              </el-button>
            </div>
          </el-form-item>

          <!-- 基本信息 -->
          <el-form-item label="平台">
            <el-select 
              v-model="form.oj_platform" 
              placeholder="选择平台"
              @change="handlePlatformChange"
            >
              <el-option label="洛谷" value="luogu" />
              <el-option label="LeetCode" value="leetcode" />
            </el-select>
          </el-form-item>

          <el-form-item label="站外ID">
            <el-input v-model="form.ext_question_id" />
          </el-form-item>

          <el-form-item label="题目名称">
            <el-input v-model="form.name" />
          </el-form-item>

          <el-form-item label="难度">
            <el-select v-model="form.difficulty" placeholder="选择难度" style="width: 100%">
              <!-- LeetCode 难度 -->
              <template v-if="form.oj_platform === 'leetcode'">
                <el-option label="简单" value="简单"></el-option>
                <el-option label="中等" value="中等"></el-option>
                <el-option label="困难" value="困难"></el-option>
              </template>
              
              <!-- 洛谷难度 -->
              <template v-else-if="form.oj_platform === 'luogu'">
                <el-option label="入门" value="入门"></el-option>
                <el-option label="普及-" value="普及-"></el-option>
                <el-option label="普及/提高-" value="普及/提高-"></el-option>
                <el-option label="普及+/提高" value="普及+/提高"></el-option>
                <el-option label="提高+/省选-" value="提高+/省选-"></el-option>
                <el-option label="省选/NOI-" value="省选/NOI-"></el-option>
                <el-option label="NOI/NOI+" value="NOI/NOI+"></el-option>
                <el-option label="CTSC" value="CTSC"></el-option>
              </template>
              
              <!-- 默认选项 -->
              <template v-else>
                <el-option label="简单" value="简单"></el-option>
                <el-option label="中等" value="中等"></el-option>
                <el-option label="困难" value="困难"></el-option>
              </template>
            </el-select>
          </el-form-item>

          <!-- 算法标签部分 -->
          <el-form-item label="已选标签">
            <div class="tags-container">
              <el-tag
                v-for="tag in selectedTags"
                :key="tag"
                closable
                :type="getTagType(tag, form.oj_platform)"
                @close="handleTagClose(tag)"
                class="algorithm-tag"
              >
                {{ getTagName(tag) }}
              </el-tag>
              <div v-if="selectedTags.length === 0" class="no-tags-hint">
                暂无已选标签，请在下方添加
              </div>
            </div>
          </el-form-item>
              
          <!-- 新增的模糊搜索标签选择 -->
          <el-form-item label="添加标签">
            <el-select
              v-model="tagSearchValue"
              filterable
              remote
              reserve-keyword
              placeholder="输入关键词搜索标签"
              :remote-method="searchTags"
              :loading="tagSearchLoading"
              @change="handleTagSelect"
              class="tag-select"
              clearable
            >
              <!-- 显示分类标题 (仅洛谷) -->
              <template v-if="form.oj_platform === 'luogu' && tagCategoryTitle">
                <el-option-group :label="tagCategoryTitle">
                  <el-option
                    v-for="tag in filteredTags"
                    :key="tag.value"
                    :label="tag.label"
                    :value="tag.value"
                  />
                </el-option-group>
              </template>
              
              <!-- 无分类标题的选项 -->
              <template v-else>
                <el-option
                  v-for="tag in filteredTags"
                  :key="tag.value"
                  :label="tag.label"
                  :value="tag.value"
                />
              </template>
            </el-select>
          </el-form-item>

          <!-- Markdown编辑器 -->
          <el-form-item label="题目描述">
            <div class="markdown-editor">
              <textarea 
                v-model="form.content" 
                class="editor-textarea"
                placeholder="输入题目描述（Markdown格式）"
              ></textarea>
            </div>
          </el-form-item>

          <!-- 按钮组 -->
          <el-form-item class="form-actions">
            <el-button type="primary" @click="saveProblem" :loading="saving">保存</el-button>
            <el-button @click="resetForm">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
      
      <!-- 右侧预览区域 -->
      <div class="preview-panel">
        <div class="preview-header">
          <h2>预览</h2>
          <div class="preview-meta">
            <div v-if="form.name" class="preview-title">{{ form.name }}</div>
            <div v-if="form.difficulty" class="preview-difficulty" :class="getDifficultyClass()">
              {{ form.difficulty }}
            </div>
          </div>
          <div class="preview-tags" v-if="selectedTags.length > 0">
            <el-tag
              v-for="tag in selectedTags"
              :key="tag"
              :type="getTagType(tag, form.oj_platform)"
              class="preview-tag"
              size="small"
            >
              {{ getTagName(tag) }}
            </el-tag>
          </div>
        </div>
        <div class="preview-content">
          <div class="markdown-preview" v-html="compiledMarkdown"></div>
          <div v-if="!form.content" class="empty-preview">
            <el-icon><Document /></el-icon>
            <p>在左侧输入内容后此处将显示预览</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import AppHeader from '@/components/AppHeader.vue'
import { Document } from '@element-plus/icons-vue'
import { extractQuestion, createQuestion, getAllTags } from '@/api/question'
import MarkdownIt from 'markdown-it'
import DOMPurify from 'dompurify'
import { ElMessage } from 'element-plus'
import { LeetcodeTags } from '@/constants/tags'

// 提前声明MathJax类型以避免no-undef错误
/* global MathJax */

export default {
  name: 'CreateView',
  components: {
    AppHeader,
    Document
  },
  data() {
    return {
      fetching: false,
      saving: false,
      mdi: new MarkdownIt({
        html: true,
        linkify: true,
        typographer: true
      }),
      form: {
        url: '',
        oj_platform: '',
        ext_question_id: '',
        name: '',
        difficulty: '',
        content: ''
      },
      mathJaxLoaded: false,
      
      // 标签相关数据
      selectedTags: [], // 已选择的标签
      tagSearchValue: '',
      tagSearchLoading: false,
      tagCategoryTitle: '',
      
      // 标签数据
      allTags: {
        leetcode: LeetcodeTags.map(tag => ({ label: tag, value: tag })),
        luogu: {
          Algorithm: [],
          Source: [],
          Time: [],
          Region: [],
          Other: []
        }
      },
      filteredTags: [], // 筛选后的标签
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
    'form.content'() {
      if (this.mathJaxLoaded) {
        this.$nextTick(() => this.renderMathJax())
      }
    }
  },
  mounted() {
    this.initMathJax()
    this.loadAllTags()
  },
  methods: {
    // 获取难度对应的CSS类名
    getDifficultyClass() {
      const difficulty = this.form.difficulty;
      if (!difficulty) return '';
      
      if (this.form.oj_platform === 'leetcode') {
        const classMap = {
          '简单': 'diff-easy',
          '中等': 'diff-medium',
          '困难': 'diff-hard'
        };
        return classMap[difficulty] || '';
      } else if (this.form.oj_platform === 'luogu') {
        if (difficulty.includes('入门')) return 'diff-easy';
        if (difficulty.includes('普及')) return 'diff-medium';
        return 'diff-hard';
      }
      
      return '';
    },
    
    // 加载所有标签
    async loadAllTags() {
      try {
        // LeetCode标签已从常量导入
        
        // 加载洛谷标签
        const res = await getAllTags()
        if (res.data && res.data.code === 200) {
          this.allTags.luogu = res.data.data
        }
      } catch (error) {
        console.error('加载标签失败:', error)
        ElMessage.error('加载标签数据失败')
      }
    },
    
    // 平台变更时重置标签搜索
    handlePlatformChange() {
      this.tagSearchValue = ''
      this.filteredTags = []
      
      // 如果切换了平台，清空已选标签
      if (this.selectedTags.length > 0) {
        if (confirm('切换平台将清空已选标签，是否继续？')) {
          this.selectedTags = []
        } else {
          // 恢复原平台
          this.form.oj_platform = this.form.oj_platform === 'leetcode' ? 'luogu' : 'leetcode'
        }
      }
    },
    
    // 标签搜索功能
    searchTags(query) {
      this.tagSearchLoading = true
      this.tagCategoryTitle = ''
      
      if (query.trim() === '') {
        this.filteredTags = []
        this.tagSearchLoading = false
        return
      }
      
      setTimeout(() => {
        if (this.form.oj_platform === 'leetcode') {
          // 搜索LeetCode标签
          this.filteredTags = this.allTags.leetcode
            .filter(tag => tag.label.toLowerCase().includes(query.toLowerCase()))
        } else if (this.form.oj_platform === 'luogu') {
          // 搜索洛谷标签，合并所有类别
          let allLuoguTags = [];
          
          // 遍历所有类别
          for (const category in this.allTags.luogu) {
            // 过滤符合条件的标签并格式化
            const matchedTags = this.allTags.luogu[category]
              .filter(tag => tag.name.toLowerCase().includes(query.toLowerCase()))
              .map(tag => ({
                label: tag.name,
                value: `${category}_${tag.name}`,
                category
              }))
            
            if (matchedTags.length) {
              this.tagCategoryTitle = this.getCategoryName(category)
              allLuoguTags = [...allLuoguTags, ...matchedTags]
            }
          }
          
          this.filteredTags = allLuoguTags
        }
        
        this.tagSearchLoading = false
      }, 200)
    },
    
    // 获取分类中文名称
    getCategoryName(category) {
      const categoryMap = {
        'Algorithm': '算法标签',
        'Source': '来源标签',
        'Time': '时间标签',
        'Region': '地区标签',
        'Other': '其他标签'
      }
      return categoryMap[category] || category
    },
    
    // 标签选择处理
    handleTagSelect(value) {
      if (!value) return
      
      // 检查是否已选择该标签
      if (this.selectedTags.includes(value)) {
        ElMessage.warning('该标签已添加')
      } else {
        this.selectedTags.push(value)
        ElMessage.success('标签添加成功')
      }
      
      // 清空选择框
      this.tagSearchValue = ''
    },
    
    // 获取标签名称（去掉前缀）
    getTagName(tag) {
      // LeetCode标签已经是纯名称
      if (this.allTags.leetcode.some(t => t.value === tag)) {
        return tag
      }
      
      // 洛谷标签去掉前缀
      const parts = tag.split('_')
      if (parts.length > 1) {
        return parts.slice(1).join('_')
      }
      return tag
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
    
    // 删除已选标签
    handleTagClose(tag) {
      this.selectedTags = this.selectedTags.filter(t => t !== tag)
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

      // 配置MathJax - 使用单引号避免转义字符警告
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
    
    async fetchQuestionInfo() {
      if (!this.form.url) {
        ElMessage.error('请输入题目URL')
        return
      }

      this.fetching = true
      try {
        const response = await extractQuestion({ url: this.form.url })
        const data = response.data
        
        // 更新基本表单数据
        this.form = {
          ...this.form,
          url: data.url || this.form.url,
          oj_platform: data.oj_platform || this.form.oj_platform,
          ext_question_id: data.ext_question_id || this.form.ext_question_id,
          name: data.name || this.form.name,
          difficulty: data.difficulty || this.form.difficulty,
          content: data.content || this.form.content
        }
        
        // 处理算法标签
        if (data.algorithm_tags && Array.isArray(data.algorithm_tags)) {
          this.selectedTags = [...data.algorithm_tags]
        }
        
        ElMessage.success('题目信息抓取成功')
      } catch (error) {
        console.error('抓取题目信息失败:', error)
        ElMessage.error('抓取题目信息失败')
      } finally {
        this.fetching = false
      }
    },
    
    async saveProblem() {
      if (!this.validateForm()) return
      
      // 准备请求数据
      const requestData = {
        ext_question_id: this.form.ext_question_id,
        name: this.form.name,
        url: this.form.url,
        oj_platform: this.form.oj_platform,
        difficulty: this.form.difficulty,
        content: this.form.content,
        algorithm_tags: this.selectedTags // 直接使用数组格式
      }
      
      this.saving = true
      try {
        const response = await createQuestion(requestData)
        const { status, message, data } = response.data
        
        if (status === 'success') {
          ElMessage.success(message || '题目创建成功')
          // 可以在这里处理返回的数据，例如跳转到详情页
          console.log('创建的题目数据:', data)
          
          // 重置表单
          this.resetForm()
        } else {
          ElMessage.error(message || '题目创建失败')
        }
      } catch (error) {
        console.error('保存题目失败:', error)
        ElMessage.error('保存题目失败: ' + (error.message || '未知错误'))
      } finally {
        this.saving = false
      }
    },
    
    validateForm() {
      if (!this.form.oj_platform) {
        ElMessage.error('请选择平台')
        return false
      }
      if (!this.form.ext_question_id) {
        ElMessage.error('请输入站外ID')
        return false
      }
      if (!this.form.name) {
        ElMessage.error('请输入题目名称')
        return false
      }
      if (!this.form.content) {
        ElMessage.error('请输入题目描述')
        return false
      }
      return true
    },
    
    resetForm() {
      this.form = {
        url: '',
        oj_platform: '',
        ext_question_id: '',
        name: '',
        difficulty: '',
        content: ''
      }
      this.selectedTags = []
      this.tagSearchValue = ''
    }
  }
}
</script>

<style scoped>
.create-view {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%);
  padding-top: 60px;
}

.layout-container {
  display: flex;
  max-width: 1600px;
  margin: 0 auto;
  gap: 24px;
  padding: 24px;
  height: calc(100vh - 60px); /* 减去顶栏高度 */
}

/* 左侧操作面板 */
.control-panel {
  flex: 1;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
}

.control-panel h1 {
  font-size: 1.8rem;
  color: #2c3e50;
  margin-bottom: 1.5rem;
  font-weight: 600;
  text-align: center;
}

/* 右侧预览区域 */
.preview-panel {
  flex: 1;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
}

.preview-header {
  padding: 16px 24px;
  border-bottom: 1px solid #eaeaea;
  background: #f8f9fa;
  border-radius: 12px 12px 0 0;
}

.preview-header h2 {
  font-size: 1.4rem;
  color: #2c3e50;
  margin-bottom: 12px;
}

.preview-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.preview-title {
  font-size: 1.2rem;
  font-weight: 600;
  color: #333;
}

.preview-difficulty {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 500;
}

.diff-easy {
  background-color: #e1f5e6;
  color: #52c41a;
}

.diff-medium {
  background-color: #fff7e6;
  color: #fa8c16;
}

.diff-hard {
  background-color: #fff1f0;
  color: #f5222d;
}

.preview-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.preview-tag {
  font-size: 0.8rem;
}

.preview-content {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  background: #fcfcfc;
}

.empty-preview {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #bbb;
  text-align: center;
}

.empty-preview .el-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.problem-form {
  width: 100%;
}

.url-input {
  display: flex;
  gap: 12px;
}

.url-input .el-input {
  flex: 1;
}

.url-input .el-button {
  min-width: 120px;
}

.el-form-item {
  margin-bottom: 18px;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  min-height: 40px;
  padding: 8px;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 6px;
}

.algorithm-tag {
  margin: 2px;
  transition: all 0.3s;
}

.algorithm-tag:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.no-tags-hint {
  color: #909399;
  font-size: 14px;
  align-self: center;
  padding: 0 10px;
}

.tag-select {
  width: 100%;
}

.markdown-editor {
  width: 100%;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
  border: 1px solid #eaeaea;
}

.editor-textarea {
  width: 100%;
  min-height: 300px;
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
  min-height: 300px;
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
.form-actions {
  margin-top: 20px;
  text-align: center;
}

.form-actions .el-button {
  min-width: 120px;
  height: 40px;
}

/* 响应式调整 */
@media (max-width: 1200px) {
  .layout-container {
    flex-direction: column;
    height: auto;
  }
  
  .control-panel, .preview-panel {
    width: 100%;
  }
  
  .preview-panel {
    min-height: 500px;
  }
}

@media (max-width: 768px) {
  .layout-container {
    padding: 16px;
  }
  
  .control-panel, .preview-panel {
    padding: 16px;
  }
  
  .url-input {
    flex-direction: column;
  }
  
  .url-input .el-button {
    width: 100%;
  }
  
  .editor-textarea,
  .markdown-preview {
    min-height: 250px;
  }
}
</style>