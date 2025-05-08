<template>
  <div class="solution-detail-view">
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
      
      <div v-else-if="solution && solution.is_deleted" class="solution-content">
        <div class="left-section">
          <el-card class="solution-description-card">
            <div class="deleted-banner">
              <el-alert
                title="此题解已被删除"
                type="warning"
                :closable="false"
              />
            </div>
            
            <h1 class="solution-title">题目 #{{ solution.question_id }} 的解题思路</h1>
            
            <div class="solution-metadata">
              <span class="solution-time">
                <i class="el-icon-time"></i>
                创建于: {{ formatDate(solution.created_at) }}
              </span>
              <span class="solution-time" v-if="solution.updated_at !== solution.created_at">
                <i class="el-icon-edit-outline"></i>
                更新于: {{ formatDate(solution.updated_at) }}
              </span>
              <span class="solution-language">
                <el-tag size="small" :class="'lang-tag-' + getNormalizedLanguage(solution.language)">
                  {{ getDisplayLanguage(solution.language) }}
                </el-tag>
              </span>
              <span class="solution-status" v-if="solution.is_draft">
                <el-tag size="small" type="info">草稿</el-tag>
              </span>
            </div>
            
            <!-- 题解内容 - Markdown渲染 -->
            <div ref="markdownContent" class="markdown-content" v-html="compiledMarkdown"></div>
          </el-card>
        </div>
        
        <div class="right-section">
          <!-- 题目信息卡片 -->
          <el-card class="question-info-card">
            <h2 @click="goToProblem(solution.question_id)" class="clickable-title">
              {{ questionDetails?.name || `题目 #${solution.question_id}` }}
              <i class="el-icon-link"></i>
            </h2>
            <div class="info-meta">
              <div>题目ID: {{ solution.question_id }}</div>
              <div v-if="questionDetails?.ext_question_id">外部ID: {{ questionDetails.ext_question_id }}</div>
              <div v-if="questionDetails?.oj_platform">
                平台: 
                <el-tag :type="getPlatformTagType(questionDetails.oj_platform)" size="small">
                  {{ getPlatformName(questionDetails.oj_platform) }}
                </el-tag>
              </div>
            </div>
            
            <div class="action-buttons" v-if="canManageSolution">
              <el-button type="primary" size="small" @click="handleRestore">
                <el-icon><RefreshLeft /></el-icon>
                恢复
              </el-button>
              <el-button type="primary" size="small" @click="handleEdit">
                <el-icon><EditPen /></el-icon>
                编辑
              </el-button>
              <el-button type="success" size="small" @click="goToProblem(solution.question_id)">
                <el-icon><View /></el-icon>
                查看题目
              </el-button>
            </div>
          </el-card>
          
          <!-- 题目标签和难度 -->
          <el-card class="question-tags-card" v-if="questionDetails">
            <div class="difficulty-section">
              <h3>难度级别</h3>
              <el-tag 
                :type="getDifficultyTagType(questionDetails)"
                effect="dark"
              >
                {{ questionDetails.difficulty }}
              </el-tag>
            </div>
            
            <div class="tags-section" v-if="questionDetails.algorithm_tags?.length">
              <h3>算法标签</h3>
              <div class="tags-container">
                <el-tag 
                  v-for="tag in questionDetails.algorithm_tags" 
                  :key="tag"
                  :type="getTagType(tag, questionDetails.oj_platform)"
                  class="algorithm-tag"
                >
                  {{ getTagName(tag) }}
                </el-tag>
              </div>
            </div>
          </el-card>
        </div>
      </div>
      
      <div v-else class="solution-content">
        <div class="left-section">
          <el-card class="solution-description-card">
            <h1 class="solution-title">题目 #{{ solution.question_id }} 的解题思路</h1>
            
            <div class="solution-metadata">
              <span class="solution-time">
                <i class="el-icon-time"></i>
                创建于: {{ formatDate(solution.created_at) }}
              </span>
              <span class="solution-time" v-if="solution.updated_at !== solution.created_at">
                <i class="el-icon-edit-outline"></i>
                更新于: {{ formatDate(solution.updated_at) }}
              </span>
              <span class="solution-language">
                <el-tag size="small" :class="'lang-tag-' + getNormalizedLanguage(solution.language)">
                  {{ getDisplayLanguage(solution.language) }}
                </el-tag>
              </span>
              <span class="solution-status" v-if="solution.is_draft">
                <el-tag size="small" type="info">草稿</el-tag>
              </span>
            </div>
            
            <!-- 题解内容 - Markdown渲染 -->
            <div ref="markdownContent" class="markdown-content" v-html="compiledMarkdown"></div>
          </el-card>
        </div>
        
        <div class="right-section">
          <!-- 题目信息卡片 -->
          <el-card class="question-info-card">
            <h2 @click="goToProblem(solution.question_id)" class="clickable-title">
              {{ questionDetails?.name || `题目 #${solution.question_id}` }}
              <i class="el-icon-link"></i>
            </h2>
            <div class="info-meta">
              <div>题目ID: {{ solution.question_id }}</div>
              <div v-if="questionDetails?.ext_question_id">外部ID: {{ questionDetails.ext_question_id }}</div>
              <div v-if="questionDetails?.oj_platform">
                平台: 
                <el-tag :type="getPlatformTagType(questionDetails.oj_platform)" size="small">
                  {{ getPlatformName(questionDetails.oj_platform) }}
                </el-tag>
              </div>
            </div>
            
            <div class="action-buttons" v-if="canManageSolution">
              <el-button type="primary" size="small" @click="handleEdit">
                <el-icon><EditPen /></el-icon>
                编辑
              </el-button>
              <el-button type="danger" size="small" @click="handleDelete">
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
              <el-button type="success" size="small" @click="goToProblem(solution.question_id)">
                <el-icon><View /></el-icon>
                查看题目
              </el-button>
            </div>
          </el-card>
          
          <!-- 题目标签和难度 -->
          <el-card class="question-tags-card" v-if="questionDetails">
            <div class="difficulty-section">
              <h3>难度级别</h3>
              <el-tag 
                :type="getDifficultyTagType(questionDetails)"
                effect="dark"
              >
                {{ questionDetails.difficulty }}
              </el-tag>
            </div>
            
            <div class="tags-section" v-if="questionDetails.algorithm_tags?.length">
              <h3>算法标签</h3>
              <div class="tags-container">
                <el-tag 
                  v-for="tag in questionDetails.algorithm_tags" 
                  :key="tag"
                  :type="getTagType(tag, questionDetails.oj_platform)"
                  class="algorithm-tag"
                >
                  {{ getTagName(tag) }}
                </el-tag>
              </div>
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
      <span>确定要删除这篇题解吗？此操作不可逆。</span>
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
      <span>确定要恢复这篇题解吗？</span>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="restoreDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmRestore" :loading="processing">确认恢复</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import AppHeader from '@/components/AppHeader.vue';
import { getSolutionDetail } from '@/api/solution';
import { getQuestionDetail } from '@/api/question';
import request from '@/api/request';
import MarkdownIt from 'markdown-it';
import DOMPurify from 'dompurify';
import { EditPen, Delete, View, RefreshLeft } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';

export default {
  name: 'SolutionDetailView',
  components: {
    AppHeader,
    EditPen,
    Delete,
    View,
    RefreshLeft
  },
  data() {
    return {
      solutionId: this.$route.params.id,
      solution: null,
      questionDetails: null,
      loading: true,
      error: null,
      mdi: new MarkdownIt({
        html: true,
        linkify: true,
        typographer: true,
        breaks: true
      }),
      
      // 当前用户信息（实际应从用户状态获取）
      currentUserId: null, // 应从用户状态获取
      
      // 删除和恢复相关状态
      deleteDialogVisible: false,
      restoreDialogVisible: false,
      processing: false,
      
      // 语言名称到显示名称的映射
      languageDisplayMap: {
        'cpp': 'C++',
        'csharp': 'C#',
        'javascript': 'JavaScript',
        'python': 'Python',
        'java': 'Java',
        'go': 'Go',
        'rust': 'Rust'
      }
    };
  },
  computed: {
    // 渲染Markdown
    compiledMarkdown() {
      if (!this.solution) return '';
      
      try {
        // 使用content_text作为Markdown内容
        const content = String(this.solution.content_text || '');
        const html = this.mdi.render(content);
        return DOMPurify.sanitize(html);
      } catch (e) {
        console.error('Markdown处理错误:', e);
        return '内容解析出错';
      }
    },
    
    // 检查当前用户是否可以管理题解（编辑、删除、恢复）
    canManageSolution() {
      // 这里应该根据实际权限检查逻辑实现
      // 例如检查当前登录用户是否是题解作者或管理员
      return true; // 为了示例，此处默认为true
    }
  },
  mounted() {
    this.fetchSolutionDetail();
  },
  methods: {
    // 获取题解详情
    async fetchSolutionDetail() {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await getSolutionDetail(this.solutionId);
        
        if (response.data && response.data.code === 200) {
          this.solution = response.data.data;
        } else {
          this.solution = response.data;
        }
        
        // 获取题目详情
        if (this.solution && this.solution.question_id) {
          await this.fetchQuestionDetail(this.solution.question_id);
        }
      } catch (error) {
        console.error('获取题解详情失败:', error);
        this.error = '获取题解详情失败: ' + (error.message || '未知错误');
      } finally {
        this.loading = false;
      }
    },
    
    // 获取题目详情
    async fetchQuestionDetail(questionId) {
      try {
        const response = await getQuestionDetail(questionId);
        
        if (response.data && response.data.code === 200) {
          this.questionDetails = response.data.data;
        } else {
          this.questionDetails = response.data;
        }
        
        // 确保算法标签是数组
        if (this.questionDetails && typeof this.questionDetails.algorithm_tags === 'string') {
          this.questionDetails.algorithm_tags = this.questionDetails.algorithm_tags
            .split(',')
            .map(tag => tag.trim())
            .filter(tag => tag.length > 0);
        }
      } catch (error) {
        console.error('获取题目详情失败:', error);
      }
    },
    
    // 编辑按钮处理
    handleEdit() {
      if (!this.solution) return;
      // 跳转到编辑页面
      this.$router.push(`/${this.solution.id}/solutions/update`);
    },
    
    // 删除按钮处理
    handleDelete() {
      if (!this.solution || this.solution.is_deleted) return;
      this.deleteDialogVisible = true;
    },
    
    // 恢复按钮处理
    handleRestore() {
      if (!this.solution) return;
      this.restoreDialogVisible = true;
    },
    
    // 确认删除
    async confirmDelete() {
      if (!this.solution) return;
      
      this.processing = true;
      try {
        const response = await request({
          url: '/api/solution/delete/',
          method: 'post',
          data: { id: this.solution.id }
        });
        
        this.deleteDialogVisible = false;
        
        ElMessage({
          type: 'success',
          message: response.message || '题解删除成功'
        });
        
        // 刷新当前页面以显示删除状态
        await this.fetchSolutionDetail();
      } catch (error) {
        console.error('删除题解失败:', error);
        
        const errorMsg = error.response?.data?.message || 
                         error.message || 
                         '删除失败: 未知错误';
        
        ElMessage({
          type: 'error',
          message: errorMsg
        });
      } finally {
        this.processing = false;
      }
    },
    
    // 确认恢复
    async confirmRestore() {
      if (!this.solution) return;
      
      this.processing = true;
      try {
        const response = await request({
          url: '/api/solution/restore/',
          method: 'post',
          data: { id: this.solution.id }
        });
        
        this.restoreDialogVisible = false;
        
        ElMessage({
          type: 'success',
          message: response.message || '题解恢复成功'
        });
        
        // 刷新当前页面以显示恢复后的状态
        await this.fetchSolutionDetail();
      } catch (error) {
        console.error('恢复题解失败:', error);
        
        const errorMsg = error.response?.data?.message || 
                         error.message || 
                         '恢复失败: 未知错误';
        
        ElMessage({
          type: 'error',
          message: errorMsg
        });
      } finally {
        this.processing = false;
      }
    },
    
    // 跳转到题目详情
    goToProblem(questionId) {
      this.$router.push(`/${questionId}/problems`);
    },
    
    // 格式化日期
    formatDate(dateString) {
      if (!dateString) return '未知时间';
      
      const date = new Date(dateString);
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      });
    },
    
    // 获取规范化后的语言名称（用于CSS类名）
    getNormalizedLanguage(language) {
      if (!language) return '';
      
      // 转为小写
      const lowercased = language.toLowerCase();
      
      // 特殊处理，比如将 'cpp' 转为 'c++'
      const reverseMap = {
        'cpp': 'c++',
        'csharp': 'c#'
      };
      
      return reverseMap[lowercased] || lowercased;
    },
    
    // 获取显示用的语言名称
    getDisplayLanguage(language) {
      if (!language) return '';
      
      // 转为小写
      const lowercased = language.toLowerCase();
      
      // 从特殊映射中获取显示名称
      if (this.languageDisplayMap[lowercased]) {
        return this.languageDisplayMap[lowercased];
      }
      
      // 首字母大写
      return language.charAt(0).toUpperCase() + language.slice(1);
    },
    
    // 平台相关方法
    getPlatformName(platform) {
      const platforms = {
        'luogu': '洛谷',
        'leetcode': 'LeetCode'
      };
      return platforms[platform] || platform;
    },
    
    // 平台标签样式
    getPlatformTagType(platform) {
      return {
        luogu: 'success',
        leetcode: 'warning'
      }[platform] || 'info';
    },
    
    // 难度标签样式
    getDifficultyTagType(question) {
      if (question.oj_platform === 'luogu') {
        const levelMap = {
          '入门': 'info',
          '普及-': 'success',
          '普及/提高-': 'success',
          '普及+/提高': 'warning',
          '提高+/省选-': 'danger',
          '省选/NOI-': 'danger',
          'NOI/NOI+': 'danger',
          'CTSC': 'danger'
        };
        return levelMap[question.difficulty] || 'info';
      }
      
      // LeetCode难度
      return {
        '简单': 'success',
        '中等': 'warning',
        '困难': 'danger'
      }[question.difficulty] || 'info';
    },
    
    // 标签样式
    getTagType(tag, platform) {
      // LeetCode标签统一为蓝色
      if (platform === 'leetcode') return 'primary';
      
      // 洛谷标签根据前缀分类
      const prefix = tag.split('_')[0];
      return {
        'Algorithm': 'primary',  // 算法 - 蓝色
        'Source': 'success',     // 来源 - 绿色
        'Time': 'warning',       // 时间 - 黄色
        'Region': 'danger',      // 地区 - 红色
        'Other': 'info'          // 其他 - 灰色
      }[prefix] || 'info';
    },
    
    // 获取标签名称
    getTagName(tag) {
      // 洛谷标签去掉前缀
      const parts = tag.split('_');
      if (parts.length > 1) {
        return parts.slice(1).join('_');
      }
      return tag;
    }
  }
};
</script>

<style scoped>
/* 基础布局优化 */
.solution-detail-view {
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

/* 已删除状态的横幅优化 */
.deleted-banner {
  margin-bottom: 1.5rem;
}

/* 主内容区网格布局 */
.solution-content {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 340px;
  gap: 2rem;
  align-items: start;
}

/* 左侧题解内容区 */
.left-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
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
}

.el-card:hover {
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

/* 题解描述卡片 */
.solution-description-card {
  padding: 2rem;
  background: white;
}

.solution-title {
  font-size: 1.8rem;
  color: #2d3748;
  margin-bottom: 1.2rem;
  font-weight: 600;
  line-height: 1.3;
  border-bottom: 1px solid #e2e8f0;
  padding-bottom: 0.8rem;
}

.solution-metadata {
  display: flex;
  flex-wrap: wrap;
  gap: 1.2rem;
  margin-bottom: 2rem;
  color: #4a5568;
  font-size: 0.95rem;
  align-items: center;
}

.solution-time {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

/* 语言标签样式 */
.lang-tag-python {
  background-color: #3776ab;
  color: white;
}

.lang-tag-java {
  background-color: #f89820;
  color: white;
}

.lang-tag-c\+\+ {
  background-color: #00599c;
  color: white;
}

.lang-tag-javascript {
  background-color: #f7df1e;
  color: #000;
}

.lang-tag-go {
  background-color: #00acd7;
  color: white;
}

.lang-tag-rust {
  background-color: #b7410e;
  color: white;
}

.lang-tag-c\# {
  background-color: #68217a;
  color: white;
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

.clickable-title {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.clickable-title:hover {
  color: #3182ce;
}

.clickable-title i {
  font-size: 0.8rem;
  opacity: 0.7;
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

/* 操作按钮组 */
.action-buttons {
  display: flex;
  flex-wrap: nowrap; /* 不允许按钮换行 */
  gap: 0.8rem;
  margin-top: 1.5rem;
  justify-content: space-between; /* 均匀分布按钮 */
  width: 100%;
}

.action-buttons .el-button {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  transition: all 0.3s ease;
  width: calc(33.33% - 0.53rem); /* 确保三个按钮大小一致 */
  min-width: 0; /* 允许按钮缩小到比内容还小 */
  white-space: nowrap; /* 文字不换行 */
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
.markdown-content {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  color: #2d3748;
  line-height: 1.7;
  font-size: 1rem;
}

/* 标题样式 */
.markdown-content :deep(h1),
.markdown-content :deep(h2),
.markdown-content :deep(h3) {
  color: #1a202c;
  font-weight: 600;
  margin: 1.8rem 0 1rem;
  scroll-margin-top: 80px; /* 为锚点跳转留出空间 */
}

.markdown-content :deep(h1) {
  font-size: 1.8rem;
  border-bottom: 1px solid #e2e8f0;
  padding-bottom: 0.5rem;
}

.markdown-content :deep(h2) {
  font-size: 1.5rem;
}

.markdown-content :deep(h3) {
  font-size: 1.2rem;
}

/* 段落样式 */
.markdown-content :deep(p) {
  margin: 1.2rem 0;
  color: #4a5568;
}

/* 代码块样式 */
.markdown-content :deep(pre) {
  background: #1e293b;
  border-radius: 8px;
  padding: 1.2rem;
  margin: 1.5rem 0;
  overflow-x: auto;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.markdown-content :deep(code) {
  font-family: 'Fira Code', 'SFMono-Regular', Consolas, monospace;
  background: transparent;
  color: #f8fafc;
  padding: 0;
  font-size: 0.9em;
}

/* 行内代码 */
.markdown-content :deep(p > code) {
  background: #edf2f7;
  color: #c53030;
  padding: 0.2em 0.4em;
  border-radius: 4px;
  font-size: 0.9em;
}

/* 引用块 */
.markdown-content :deep(blockquote) {
  border-left: 4px solid #4299e1;
  background: #ebf8ff;
  color: #2b6cb0;
  padding: 1rem 1.5rem;
  margin: 1.5rem 0;
  border-radius: 0 4px 4px 0;
}

/* 表格样式 */
.markdown-content :deep(table) {
  width: 100%;
  margin: 1.5rem 0;
  border-collapse: collapse;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.markdown-content :deep(th),
.markdown-content :deep(td) {
  border: 1px solid #e2e8f0;
  padding: 0.75rem 1rem;
  text-align: left;
}

.markdown-content :deep(th) {
  background: #f7fafc;
  font-weight: 600;
  color: #2d3748;
}

/* 列表样式 */
.markdown-content :deep(ul),
.markdown-content :deep(ol) {
  margin: 1.5rem 0;
  padding-left: 2rem;
}

.markdown-content :deep(li) {
  margin: 0.5rem 0;
  color: #4a5568;
}

/* 链接样式 */
.markdown-content :deep(a) {
  color: #4299e1;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.2s;
}

.markdown-content :deep(a:hover) {
  color: #2b6cb0;
  text-decoration: underline;
}

/* 图片样式 */
.markdown-content :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 6px;
  margin: 1.5rem auto;
  display: block;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
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
  .solution-content {
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
  
  .solution-description-card,
  .question-info-card,
  .question-tags-card {
    padding: 1.2rem;
  }
  
  .solution-title {
    font-size: 1.5rem;
  }
}

@media (max-width: 480px) {
  .action-buttons {
    flex-direction: row; /* 强制水平排列 */
    flex-wrap: nowrap;
  }
  
  .action-buttons .el-button {
    font-size: 0.75rem; /* 减小字体大小 */
    padding: 8px 12px; /* 调整内边距 */
    width: calc(33.33% - 0.53rem); /* 保持宽度均匀 */
  }
  
  .action-buttons .el-button .el-icon {
    margin-right: 2px; /* 减小图标间距 */
  }
  
  .solution-metadata {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.8rem;
  }
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