<template>
  <div class="draft-detail-view">
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
      
      <div v-else-if="draft && draft.is_deleted" class="draft-content">
        <div class="left-section">
          <el-card class="draft-description-card">
            <div class="deleted-banner">
              <el-alert
                title="此草稿已被删除"
                type="warning"
                :closable="false"
              />
            </div>
            
            <h1 class="draft-title">题目 #{{ draft.question_id }} 的解题思路（草稿）</h1>
            
            <div class="draft-metadata">
              <span class="draft-time">
                <i class="el-icon-time"></i>
                创建于: {{ formatDate(draft.created_at) }}
              </span>
              <span class="draft-time" v-if="draft.updated_at !== draft.created_at">
                <i class="el-icon-edit-outline"></i>
                更新于: {{ formatDate(draft.updated_at) }}
              </span>
              <span class="draft-language">
                <el-tag size="small" :class="'lang-tag-' + getNormalizedLanguage(draft.language)">
                  {{ getDisplayLanguage(draft.language) }}
                </el-tag>
              </span>
              <span class="draft-status">
                <el-tag size="small" type="warning">已删除</el-tag>
                <el-tag size="small" type="info">草稿</el-tag>
              </span>
            </div>
            
            <!-- 草稿内容 - Markdown渲染 -->
            <div ref="markdownContent" class="markdown-content" v-html="compiledMarkdown"></div>
          </el-card>
        </div>
        
        <div class="right-section">
          <!-- 题目信息卡片 -->
          <el-card class="question-info-card">
            <h2 @click="goToProblem(draft.question_id)" class="clickable-title">
              {{ questionDetails?.name || `题目 #${draft.question_id}` }}
              <i class="el-icon-link"></i>
            </h2>
            <div class="info-meta">
              <div>题目ID: {{ draft.question_id }}</div>
              <div v-if="questionDetails?.ext_question_id">外部ID: {{ questionDetails.ext_question_id }}</div>
              <div v-if="questionDetails?.oj_platform">
                平台: 
                <el-tag :type="getPlatformTagType(questionDetails.oj_platform)" size="small">
                  {{ getPlatformName(questionDetails.oj_platform) }}
                </el-tag>
              </div>
            </div>
            
            <div class="action-buttons" v-if="canManageDraft">
              <!-- 对已删除草稿显示恢复、编辑和查看题目按钮 -->
              <el-button type="warning" size="small" @click="handleRestore">
                <el-icon><RefreshLeft /></el-icon>
                恢复
              </el-button>
              <el-button type="primary" size="small" @click="handleEdit">
                <el-icon><EditPen /></el-icon>
                编辑
              </el-button>
              <el-button type="info" size="small" @click="goToProblem(draft.question_id)">
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
      
      <div v-else class="draft-content">
        <div class="left-section">
          <el-card class="draft-description-card">
            <h1 class="draft-title">题目 #{{ draft.question_id }} 的解题思路（草稿）</h1>
            
            <div class="draft-metadata">
              <span class="draft-time">
                <i class="el-icon-time"></i>
                创建于: {{ formatDate(draft.created_at) }}
              </span>
              <span class="draft-time" v-if="draft.updated_at !== draft.created_at">
                <i class="el-icon-edit-outline"></i>
                更新于: {{ formatDate(draft.updated_at) }}
              </span>
              <span class="draft-language">
                <el-tag size="small" :class="'lang-tag-' + getNormalizedLanguage(draft.language)">
                  {{ getDisplayLanguage(draft.language) }}
                </el-tag>
              </span>
              <span class="draft-status">
                <el-tag size="small" type="info">草稿</el-tag>
              </span>
            </div>
            
            <!-- 草稿内容 - Markdown渲染 -->
            <div ref="markdownContent" class="markdown-content" v-html="compiledMarkdown"></div>
          </el-card>
        </div>
        
        <div class="right-section">
          <!-- 题目信息卡片 -->
          <el-card class="question-info-card">
            <h2 @click="goToProblem(draft.question_id)" class="clickable-title">
              {{ questionDetails?.name || `题目 #${draft.question_id}` }}
              <i class="el-icon-link"></i>
            </h2>
            <div class="info-meta">
              <div>题目ID: {{ draft.question_id }}</div>
              <div v-if="questionDetails?.ext_question_id">外部ID: {{ questionDetails.ext_question_id }}</div>
              <div v-if="questionDetails?.oj_platform">
                平台: 
                <el-tag :type="getPlatformTagType(questionDetails.oj_platform)" size="small">
                  {{ getPlatformName(questionDetails.oj_platform) }}
                </el-tag>
              </div>
            </div>
            
            <div class="action-buttons" v-if="canManageDraft">
              <!-- 发布按钮（只在草稿未删除时显示） -->
              <el-button v-if="!draft.is_deleted" type="success" size="small" @click="handlePublish">
                <el-icon><Upload /></el-icon>
                发布
              </el-button>
              <el-button type="primary" size="small" @click="handleEdit">
                <el-icon><EditPen /></el-icon>
                编辑
              </el-button>
              <el-button v-if="!draft.is_deleted" type="danger" size="small" @click="handleDelete">
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
              <el-button v-if="draft.is_deleted" type="warning" size="small" @click="handleRestore">
                <el-icon><RefreshLeft /></el-icon>
                恢复
              </el-button>
              <el-button type="info" size="small" @click="goToProblem(draft.question_id)">
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
      <span>确定要删除这篇草稿吗？此操作不可逆。</span>
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
      <span>确定要恢复这篇草稿吗？</span>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="restoreDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmRestore" :loading="processing">确认恢复</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 发布确认对话框 -->
    <el-dialog
      v-model="publishDialogVisible"
      title="确认发布"
      width="30%"
    >
      <span>确定要将此草稿发布为正式题解吗？</span>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="publishDialogVisible = false">取消</el-button>
          <el-button type="success" @click="confirmPublish" :loading="processing">确认发布</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import AppHeader from '@/components/AppHeader.vue';
import { getDraftDetail } from '@/api/solution'; // 使用solution API获取草稿
import { getQuestionDetail } from '@/api/question';
import request from '@/api/request';
import MarkdownIt from 'markdown-it';
import DOMPurify from 'dompurify';
import { EditPen, Delete, View, RefreshLeft, Upload } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';

export default {
  name: 'DraftDetailView',
  components: {
    AppHeader,
    EditPen,
    Delete,
    View,
    RefreshLeft,
    Upload
  },
  data() {
    return {
      draftId: this.$route.params.id,
      draft: null,
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
      
      // 删除、恢复和发布相关状态
      deleteDialogVisible: false,
      restoreDialogVisible: false,
      publishDialogVisible: false,
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
      if (!this.draft) return '';
      
      try {
        // 使用content_text作为Markdown内容
        const content = String(this.draft.content_text || '');
        const html = this.mdi.render(content);
        return DOMPurify.sanitize(html);
      } catch (e) {
        console.error('Markdown处理错误:', e);
        return '内容解析出错';
      }
    },
    
    // 检查当前用户是否可以管理草稿（编辑、删除、恢复、发布）
    canManageDraft() {
      // 这里应该根据实际权限检查逻辑实现
      // 例如检查当前登录用户是否是草稿作者或管理员
      return true; // 为了示例，此处默认为true
    }
  },
  mounted() {
    this.fetchDraftDetail();
  },
  methods: {
    // 获取草稿详情
    async fetchDraftDetail() {
      this.loading = true;
      this.error = null;
      
      try {
        // 使用getSolutionDetail API但访问的是草稿路径
        const response = await getDraftDetail(this.draftId, true); // 添加参数表示获取草稿
        
        if (response.data && response.data.code === 200) {
          this.draft = response.data.data;
        } else {
          this.draft = response.data;
        }
        
        // 获取题目详情
        if (this.draft && this.draft.question_id) {
          await this.fetchQuestionDetail(this.draft.question_id);
        }
      } catch (error) {
        console.error('获取草稿详情失败:', error);
        this.error = '获取草稿详情失败: ' + (error.message || '未知错误');
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
      if (!this.draft) return;
      // 跳转到编辑页面
      this.$router.push(`/${this.draft.id}/drafts/update`);
    },
    
    // 删除按钮处理
    handleDelete() {
      if (!this.draft || this.draft.is_deleted) return;
      this.deleteDialogVisible = true;
    },
    
    // 恢复按钮处理
    handleRestore() {
      if (!this.draft) return;
      this.restoreDialogVisible = true;
    },
    
    // 发布按钮处理
    handlePublish() {
      if (!this.draft || this.draft.is_deleted) return;
      this.publishDialogVisible = true;
    },
    
    // 确认删除
    async confirmDelete() {
      if (!this.draft) return;
      
      this.processing = true;
      try {
        const response = await request({
          url: '/api/solution/delete/',
          method: 'post',
          data: { id: this.draft.id }
        });
        
        this.deleteDialogVisible = false;
        
        ElMessage({
          type: 'success',
          message: response.message || '草稿删除成功'
        });
        
        // 刷新当前页面以显示删除状态
        await this.fetchDraftDetail();
      } catch (error) {
        console.error('删除草稿失败:', error);
        
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
      if (!this.draft) return;
      
      this.processing = true;
      try {
        const response = await request({
          url: '/api/solution/restore/',
          method: 'post',
          data: { id: this.draft.id }
        });
        
        this.restoreDialogVisible = false;
        
        ElMessage({
          type: 'success',
          message: response.message || '草稿恢复成功'
        });
        
        // 刷新当前页面以显示恢复后的状态
        await this.fetchDraftDetail();
      } catch (error) {
        console.error('恢复草稿失败:', error);
        
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
    
    // 确认发布为题解
    async confirmPublish() {
      if (!this.draft || this.draft.is_deleted) return;
      
      this.processing = true;
      try {
        // 1. 发送请求（注意解构出data）
        const { data: responseData } = await request({
          url: '/api/solution/pub/',
          method: 'post',
          data: { id: this.draft.id }
        });

        // 2. 关闭对话框
        this.publishDialogVisible = false;
        
        // 3. 处理响应（现在正确检查responseData.code）
        if (responseData.code === 200) {
          ElMessage({
            type: 'success',
            message: responseData.message || '发布成功'
          });
          
          // 4. 跳转逻辑（正确获取嵌套的id）
          const solutionId = responseData.data?.id;
          if (solutionId) {
            this.$router.push(`/${solutionId}/solutions`);
          } else {
            this.$router.push('/solutions');
          }
        } else {
          // 5. 处理业务错误（正确获取错误消息）
          throw new Error(responseData.message || `发布失败，错误码：${responseData.code}`);
        }
      } catch (error) {
        // 6. 统一错误处理
        console.error('发布失败:', error);
        ElMessage({
          type: 'error',
          message: error.message || '发布过程中发生未知错误'
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
.draft-detail-view {
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
.draft-content {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 340px;
  gap: 2rem;
  align-items: start;
}

/* 左侧草稿内容区 */
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

/* 草稿描述卡片 */
.draft-description-card {
  padding: 2rem;
  background: white;
}

.draft-title {
  font-size: 1.8rem;
  color: #2d3748;
  margin-bottom: 1.2rem;
  font-weight: 600;
  line-height: 1.3;
  border-bottom: 1px solid #e2e8f0;
  padding-bottom: 0.8rem;
}

.draft-metadata {
  display: flex;
  flex-wrap: wrap;
  gap: 1.2rem;
  margin-bottom: 2rem;
  color: #4a5568;
  font-size: 0.95rem;
  align-items: center;
}

.draft-time {
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
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.8rem;
  margin-top: 1.5rem;
}

.action-buttons .el-button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  transition: all 0.3s ease;
  min-width: 0;
  white-space: nowrap;
  padding: 8px 15px;
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
  .draft-content {
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
    flex-wrap: wrap;
  }
  
  .draft-description-card,
  .question-info-card,
  .question-tags-card {
    padding: 1.2rem;
  }
  
  .draft-title {
    font-size: 1.5rem;
  }
}

@media (max-width: 480px) {
  .action-buttons {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 0.5rem;
  }
  
  .action-buttons .el-button {
    width: 100%;
    padding: 8px 12px;
    font-size: 0.8rem;
  }
  
  .draft-metadata {
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