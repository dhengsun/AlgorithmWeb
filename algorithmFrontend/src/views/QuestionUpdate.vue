<template>
  <div class="question-update-view">
    <AppHeader />
    <main class="page-container">
      <el-card class="update-card">
        <template #header>
          <div class="card-header">
            <h2>更新题目</h2>
          </div>
        </template>

        <!-- 题目ID查询部分 -->
        <div v-if="!question" class="id-query-section">
          <el-form :model="queryForm" :rules="queryRules" ref="queryFormRef" label-width="80px">
            <el-form-item label="题目ID" prop="id">
              <el-input v-model="queryForm.id" placeholder="请输入题目ID（如E1、E2等）"></el-input>
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="fetchQuestion">查询题目</el-button>
            </el-form-item>
          </el-form>
        </div>

        <!-- 加载中状态 -->
        <div v-else-if="loading" class="loading-container">
          <el-skeleton :rows="10" animated />
        </div>

        <!-- 错误提示 -->
        <div v-else-if="error" class="error-container">
          <el-alert
            :title="error"
            type="error"
            :closable="false"
            @close="resetQuery"
          />
          <el-button class="mt-3" @click="resetQuery">返回</el-button>
        </div>

        <!-- 题目编辑表单 -->
        <div v-else class="question-form-container">
          <el-form 
            :model="questionForm" 
            :rules="rules" 
            ref="formRef" 
            label-width="100px"
            label-position="top"
          >
            <!-- 基本信息部分 -->
            <el-divider content-position="left">基本信息</el-divider>
            
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="题目名称" prop="name">
                  <el-input v-model="questionForm.name" placeholder="请输入题目名称"></el-input>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="外部ID" prop="ext_question_id">
                  <el-input v-model="questionForm.ext_question_id" placeholder="请输入外部ID"></el-input>
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="平台" prop="oj_platform">
                  <el-select 
                    v-model="questionForm.oj_platform" 
                    placeholder="请选择平台" 
                    style="width: 100%"
                    @change="handlePlatformChange"
                  >
                    <el-option label="LeetCode" value="leetcode"></el-option>
                    <el-option label="洛谷" value="luogu"></el-option>
                    <!-- 可以添加更多平台 -->
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="难度" prop="difficulty">
                  <el-select 
                    v-model="questionForm.difficulty" 
                    placeholder="请选择难度" 
                    style="width: 100%"
                  >
                    <!-- LeetCode 难度 -->
                    <template v-if="questionForm.oj_platform === 'leetcode'">
                      <el-option label="简单" value="简单"></el-option>
                      <el-option label="中等" value="中等"></el-option>
                      <el-option label="困难" value="困难"></el-option>
                    </template>
                    
                    <!-- 洛谷难度 -->
                    <template v-else-if="questionForm.oj_platform === 'luogu'">
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
              </el-col>
            </el-row>

            <!-- 算法标签部分 -->
            <el-divider content-position="left">算法标签</el-divider>
            <el-form-item label="已选标签" prop="algorithm_tags">
              <div class="tags-container">
                <el-tag
                  v-for="tag in questionForm.algorithm_tags"
                  :key="tag"
                  closable
                  :type="getTagType(tag, questionForm.oj_platform)"
                  @close="handleTagClose(tag)"
                  class="algorithm-tag"
                >
                  {{ getTagName(tag) }}
                </el-tag>
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
                <template v-if="questionForm.oj_platform === 'luogu' && tagCategoryTitle">
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

            <!-- 题目内容部分 -->
            <el-divider content-position="left">题目内容</el-divider>
            <el-form-item 
              label="题目内容" 
              prop="content"
              :rules="[{ required: true, message: '题目内容不能为空', trigger: 'blur' }]"
            >
              <el-tabs v-model="contentTabActive">
                <el-tab-pane label="编辑" name="edit">
                  <el-input
                    v-model="questionForm.content"
                    type="textarea"
                    :rows="15"
                    placeholder="请输入题目内容"
                  ></el-input>
                </el-tab-pane>
                <el-tab-pane label="预览" name="preview">
                  <div v-if="questionForm.oj_platform === 'leetcode'" 
                       class="preview-container html-content" 
                       v-html="previewHtml">
                  </div>
                  <div v-else 
                       class="preview-container markdown-content" 
                       v-html="previewMarkdown">
                  </div>
                </el-tab-pane>
              </el-tabs>
            </el-form-item>

            <!-- 操作按钮 -->
            <el-form-item>
              <el-button type="primary" @click="submitForm">更新题目</el-button>
              <el-button @click="resetForm">重置表单</el-button>
              <el-button type="info" @click="resetQuery">返回查询</el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-card>
    </main>
  </div>
</template>

<script>
import AppHeader from '@/components/AppHeader.vue'
import { getQuestionDetail, getAllTags } from '@/api/question'
import MarkdownIt from 'markdown-it'
import DOMPurify from 'dompurify'
import { ElMessage } from 'element-plus'

// 导入更新题目的API和标签常量
import { updateQuestion } from '@/api/question'
import { LeetcodeTags } from '@/constants/tags'

export default {
  name: 'QuestionUpdate',
  components: {
    AppHeader
  },
  data() {
    return {
      // 查询表单
      queryForm: {
        id: ''
      },
      queryRules: {
        id: [
          { required: true, message: '请输入题目ID', trigger: 'blur' },
          // 修改验证规则，允许字母和数字的组合
          { pattern: /^[a-zA-Z0-9]+$/, message: '题目ID只能包含字母和数字', trigger: 'blur' }
        ]
      },
      
      // 题目状态
      question: null,
      loading: false,
      error: null,
      
      // 题目表单
      questionForm: {
        id: '',
        name: '',
        ext_question_id: '',
        oj_platform: '',
        difficulty: '',
        algorithm_tags: [],
        content: ''
      },
      
      // 表单验证规则
      rules: {
        name: [
          { required: true, message: '请输入题目名称', trigger: 'blur' },
          { min: 1, max: 100, message: '长度在1到100个字符', trigger: 'blur' }
        ],
        ext_question_id: [
          { required: true, message: '请输入外部ID', trigger: 'blur' }
        ],
        oj_platform: [
          { required: true, message: '请选择平台', trigger: 'change' }
        ],
        difficulty: [
          { required: true, message: '请选择难度', trigger: 'change' }
        ]
      },
      
      // 标签相关数据
      tagInputVisible: false,
      tagInputValue: '',
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
      
      // 内容预览标签页
      contentTabActive: 'edit',
      
      // Markdown渲染
      mdi: new MarkdownIt({
        html: true,
        linkify: true,
        typographer: true
      }),
    }
  },
  computed: {
    // Markdown预览
    previewMarkdown() {
      if (!this.questionForm.content) return ''
      
      try {
        const content = String(this.questionForm.content || '')
        const html = this.mdi.render(content)
        return DOMPurify.sanitize(html)
      } catch (e) {
        console.error('Markdown处理错误:', e)
        return '内容解析出错'
      }
    },
    
    // HTML预览
    previewHtml() {
      if (!this.questionForm.content) return ''
      
      try {
        let content = String(this.questionForm.content || '')
        
        // 简单处理HTML内容
        return DOMPurify.sanitize(content, {
          USE_PROFILES: { html: true },
          ALLOWED_TAGS: [
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'br', 'hr',
            'ol', 'ul', 'li', 'pre', 'code', 'blockquote',
            'table', 'thead', 'tbody', 'tr', 'th', 'td',
            'strong', 'em', 'b', 'i', 'u', 'strike', 's',
            'a', 'img', 'span', 'div', 'section', 'article'
          ]
        })
      } catch (e) {
        console.error('HTML处理错误:', e)
        return '内容解析出错'
      }
    }
  },
  mounted() {
    // 加载所有平台的标签
    this.loadAllTags()
    
    // 如果URL中带有id参数，则自动填充并查询
    const urlId = this.$route.params.id
    if (urlId) {
      this.queryForm.id = urlId
      this.fetchQuestion()
    }
  },
  methods: {
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
      if (confirm('切换平台将清空已选标签，是否继续？')) {
        this.questionForm.algorithm_tags = []
      } else {
        // 恢复原平台
        this.questionForm.oj_platform = this.question.oj_platform
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
        if (this.questionForm.oj_platform === 'leetcode') {
          // 搜索LeetCode标签
          this.filteredTags = this.allTags.leetcode
            .filter(tag => tag.label.toLowerCase().includes(query.toLowerCase()))
        } else if (this.questionForm.oj_platform === 'luogu') {
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
      if (this.questionForm.algorithm_tags.includes(value)) {
        ElMessage.warning('该标签已添加')
      } else {
        this.questionForm.algorithm_tags.push(value)
        ElMessage.success('标签添加成功')
      }
      
      // 清空选择框
      this.tagSearchValue = ''
    },
    
    // 查询题目
    async fetchQuestion() {
      // 表单验证
      try {
        await this.$refs.queryFormRef.validate()
      } catch (error) {
        return false
      }
      
      this.loading = true
      this.error = null
      
      try {
        const response = await getQuestionDetail(this.queryForm.id)
        this.question = response.data
        
        // 填充表单
        this.fillFormWithQuestion(this.question)
        
        this.loading = false
      } catch (error) {
        console.error('获取题目详情失败:', error)
        this.error = '获取题目详情失败: ' + (error.message || '未知错误')
        this.loading = false
      }
    },
    
    // 填充表单
    fillFormWithQuestion(question) {
      this.questionForm.id = question.id
      this.questionForm.name = question.name
      this.questionForm.ext_question_id = question.ext_question_id
      this.questionForm.oj_platform = question.oj_platform
      this.questionForm.difficulty = question.difficulty
      this.questionForm.content = question.content
      
      // 处理标签
      if (typeof question.algorithm_tags === 'string') {
        this.questionForm.algorithm_tags = question.algorithm_tags
          .split(',')
          .map(tag => tag.trim())
          .filter(tag => tag.length > 0)
      } else if (Array.isArray(question.algorithm_tags)) {
        this.questionForm.algorithm_tags = [...question.algorithm_tags]
      } else {
        this.questionForm.algorithm_tags = []
      }
    },
    
    // 重置查询
    resetQuery() {
      this.question = null
      this.error = null
      this.queryForm.id = ''
      
      if (this.$refs.queryFormRef) {
        this.$refs.queryFormRef.resetFields()
      }
    },
    
    // 重置表单
    resetForm() {
      if (this.$refs.formRef) {
        this.$refs.formRef.resetFields()
      }
      
      // 重新填充原始数据
      if (this.question) {
        this.fillFormWithQuestion(this.question)
      }
    },
    
    // 提交表单
    async submitForm() {
      // 表单验证
      try {
        await this.$refs.formRef.validate()
      } catch (error) {
        return false
      }
      
      this.loading = true
      
      try {
        // 创建适合后端API的请求数据
        const formData = {
          id: this.questionForm.id,
          name: this.questionForm.name,
          ext_question_id: this.questionForm.ext_question_id,
          oj_platform: this.questionForm.oj_platform,
          difficulty: this.questionForm.difficulty,
          content: this.questionForm.content,
          // 确保算法标签是数组形式，与Postman测试保持一致
          algorithm_tags: Array.isArray(this.questionForm.algorithm_tags) 
            ? [...this.questionForm.algorithm_tags] 
            : []
        }
        
        // 可以添加url字段，如果后端需要
        if (this.questionForm.oj_platform === 'leetcode') {
          formData.url = `https://leetcode.cn/problems/${this.questionForm.ext_question_id}/`
        } else if (this.questionForm.oj_platform === 'luogu') {
          formData.url = `https://www.luogu.com.cn/problem/${this.questionForm.ext_question_id}`
        }
        
        console.log('发送更新请求数据:', formData)
        
        // 调用更新API
        await updateQuestion(formData.id, formData)
        
        // 显示成功消息
        ElMessage({
          message: '题目更新成功',
          type: 'success'
        })
        
        // 重新获取最新数据
        this.fetchQuestion()
      } catch (error) {
        console.error('更新题目失败:', error)
        ElMessage({
          message: '更新题目失败: ' + (error.message || '未知错误'),
          type: 'error'
        })
      } finally {
        this.loading = false
      }
    },
    
    // 删除已选标签
    handleTagClose(tag) {
      this.questionForm.algorithm_tags = this.questionForm.algorithm_tags.filter(t => t !== tag)
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
    }
  }
}
</script>

<style scoped>
.question-update-view {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%);
  padding-top: 60px;
}

.page-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 30px;
}

.update-card {
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: none;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(5px);
}

.card-header {
  padding: 20px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.card-header h2 {
  font-size: 1.5rem;
  color: #2c3e50;
  font-weight: 600;
  margin: 0;
}

.id-query-section,
.question-form-container {
  padding: 25px;
}

.loading-container,
.error-container {
  padding: 40px;
  text-align: center;
}

/* 表单样式优化 */
.el-form {
  max-width: 900px;
  margin: 0 auto;
}

.el-form-item {
  margin-bottom: 22px;
}

.el-form-item:last-child {
  margin-bottom: 0;
}

.el-input,
.el-select,
.el-textarea {
  border-radius: 8px;
}

.el-textarea__inner {
  min-height: 300px;
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
  line-height: 1.6;
}

/* 分割线样式 */
.el-divider__text {
  font-size: 1rem;
  color: #606266;
  font-weight: 500;
}

/* 标签容器 */
.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  padding: 12px;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 8px;
  min-height: 48px;
}

.algorithm-tag {
  transition: all 0.3s;
  margin: 0;
}

.algorithm-tag:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

/* 标签选择器 */
.tag-select {
  width: 100%;
}

/* 预览区域 */
.preview-container {
  padding: 20px;
  border-radius: 8px;
  background: #fff;
  min-height: 300px;
  max-height: 500px;
  overflow-y: auto;
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.05);
}

/* Markdown/HTML内容样式 */
.markdown-content,
.html-content {
  line-height: 1.8;
}

.markdown-content :deep(h1),
.markdown-content :deep(h2),
.markdown-content :deep(h3),
.html-content :deep(h1),
.html-content :deep(h2),
.html-content :deep(h3) {
  margin-top: 1.5em;
  margin-bottom: 0.8em;
  color: #2c3e50;
  font-weight: 600;
}

.markdown-content :deep(pre),
.html-content :deep(pre) {
  background-color: #f8f9fa;
  padding: 16px;
  border-radius: 8px;
  overflow: auto;
  border-left: 4px solid #409eff;
}

.markdown-content :deep(code),
.html-content :deep(code) {
  background-color: rgba(175, 184, 193, 0.2);
  padding: 0.2em 0.4em;
  border-radius: 4px;
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
  color: #476582;
}

.markdown-content :deep(blockquote),
.html-content :deep(blockquote) {
  border-left: 4px solid #dfe2e5;
  color: #6a737d;
  padding: 0 1em;
  margin: 1em 0;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 0 4px 4px 0;
}

.markdown-content :deep(table),
.html-content :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 1.5em 0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.markdown-content :deep(th),
.html-content :deep(th) {
  background-color: #f8f9fa;
  font-weight: 600;
}

.markdown-content :deep(th),
.markdown-content :deep(td),
.html-content :deep(th),
.html-content :deep(td) {
  border: 1px solid #dfe2e5;
  padding: 12px 16px;
  text-align: left;
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

/* 响应式调整 */
@media (max-width: 768px) {
  .page-container {
    padding: 15px;
  }

  .id-query-section,
  .question-form-container {
    padding: 15px;
  }

  .el-form-item:last-child .el-button {
    width: 100%;
    margin: 8px 0;
  }

  .el-col {
    margin-bottom: 16px;
  }
}

/* 动画效果 */
.el-tag,
.el-button {
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.1);
}

.el-tag:hover {
  transform: translateY(-2px);
}

.el-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

/* 标签页样式优化 */
:deep(.el-tabs__nav-wrap) {
  padding: 0 20px;
  background: #f8f9fa;
  border-radius: 8px 8px 0 0;
}

:deep(.el-tabs__item) {
  padding: 0 24px;
  height: 48px;
  line-height: 48px;
  font-weight: 500;
}

:deep(.el-tabs__content) {
  padding: 0;
}
</style>