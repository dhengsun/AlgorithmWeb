<template>
  <div class="solution-update-view">
    <AppHeader />
    <main class="page-container">
      <h1>编辑题解</h1>
      
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
      
      <div v-else class="solution-content">
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
            <el-select v-model="form.language" placeholder="选择编程语言" class="w-100">
              <el-option
                v-for="item in languageOptions"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              />
            </el-select>
          </el-form-item>
          
          <!-- 草稿状态切换 -->
          <el-form-item label="是否为草稿">
            <el-switch v-model="form.is_draft" />
          </el-form-item>

          <!-- Markdown编辑器 -->
          <el-form-item label="题解内容">
            <div class="markdown-editor">
              <el-tabs v-model="activeTab">
                <el-tab-pane label="编辑" name="edit">
                  <textarea 
                    v-model="form.content_text" 
                    class="editor-textarea"
                    placeholder="输入题解内容（Markdown格式）"
                  ></textarea>
                </el-tab-pane>
                <el-tab-pane label="预览" name="preview">
                  <div ref="markdownPreview" class="markdown-preview" v-html="compiledMarkdown"></div>
                </el-tab-pane>
              </el-tabs>
            </div>
          </el-form-item>

          <!-- 按钮组 -->
          <el-form-item>
            <el-button type="primary" @click="handleSubmit" :loading="submitting">更新</el-button>
            <el-button @click="handleReset" :disabled="submitting">重置</el-button>
            <el-button type="danger" @click="handleDelete" :disabled="submitting">删除</el-button>
          </el-form-item>
        </el-form>
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
  </div>
</template>

<script>
import AppHeader from '@/components/AppHeader.vue';
import { getSolutionDetail, updateSolution } from '@/api/solution';
import { getQuestionDetail } from '@/api/question';
import request from '@/api/request';
import MarkdownIt from 'markdown-it';
import DOMPurify from 'dompurify';
import { ElMessage } from 'element-plus';

// 提前声明MathJax类型以避免no-undef错误
/* global MathJax */

export default {
  name: 'SolutionUpdateView',
  components: {
    AppHeader
  },
  data() {
    return {
      solutionId: this.$route.params.id, // 从路由参数获取ID
      originalSolution: null, // 用于重置
      loading: true,
      error: null,
      submitting: false,
      processing: false,
      fetching: false,
      deleteDialogVisible: false,
      mathJaxLoaded: false,
      activeTab: 'edit',
      
      // 表单数据
      form: {
        question_id: '',
        question_name: '',
        language: '',
        content_text: '',
        is_draft: false
      },
      
      // Markdown渲染器
      mdi: new MarkdownIt({
        html: true,
        linkify: true,
        typographer: true,
        breaks: true
      }),
      
      // 语言选项
      languageOptions: [
        { value: 'python', label: 'Python' },
        { value: 'java', label: 'Java' },
        { value: 'cpp', label: 'C++' },
        { value: 'javascript', label: 'JavaScript' },
        { value: 'csharp', label: 'C#' },
        { value: 'go', label: 'Go' },
        { value: 'rust', label: 'Rust' }
      ]
    };
  },
  computed: {
    // 预览 - Markdown渲染
    compiledMarkdown() {
      try {
        const content = String(this.form.content_text || '');
        const html = this.mdi.render(content);
        return DOMPurify.sanitize(html);
      } catch (e) {
        console.error('Markdown处理错误:', e);
        return '内容解析出错';
      }
    }
  },
  watch: {
    activeTab(newVal) {
      if (newVal === 'preview') {
        this.initMathJax();
        this.$nextTick(() => this.renderMathJax());
      }
    },
    'form.content_text'() {
      if (this.activeTab === 'preview' && this.mathJaxLoaded) {
        this.$nextTick(() => this.renderMathJax());
      }
    }
  },
  created() {
    console.log("组件创建，题解ID:", this.solutionId);
  },
  mounted() {
    console.log("组件挂载，获取题解ID:", this.solutionId);
    this.fetchSolutionDetail(); // 组件挂载时加载题解数据
    this.initMathJax();
  },
  methods: {
    // 获取题解详情 - 根据ID加载现有题解
    async fetchSolutionDetail() {
      this.loading = true;
      this.error = null;
      
      try {
        console.log("正在获取题解详情，ID:", this.solutionId);
        const response = await getSolutionDetail(this.solutionId);
        
        // 打印完整响应以调试
        console.log("题解API返回完整响应:", JSON.stringify(response));
        
        // 处理可能的响应结构
        let solutionData = response;
        
        if (response.data) {
          if (response.data.code === 200) {
            solutionData = response.data.data;
          } else {
            solutionData = response.data;
          }
        }
        
        console.log("提取的题解数据:", JSON.stringify(solutionData));
        
        // 保存原始数据用于重置
        this.originalSolution = { ...solutionData };
        
        // 检查并打印所有可能的字段名
        console.log("数据字段名称检查:");
        for (const key in solutionData) {
          console.log(`- ${key}: ${JSON.stringify(solutionData[key])}`);
        }
        
        // 填充表单，检查所有可能的字段名称变体
        this.form = {
          question_id: solutionData.question_id || '',
          question_name: solutionData.question_name || '',
          language: solutionData.language || '',
          content_text: solutionData.content_text || solutionData.content || '',
          is_draft: !!solutionData.is_draft
        };
        
        console.log("表单数据已填充:", JSON.stringify(this.form));
        
        // 如果没有题目名称，则获取题目详情
        if (this.form.question_id && !this.form.question_name) {
          await this.fetchQuestionInfo();
        }
        
      } catch (error) {
        console.error('获取题解详情失败:', error);
        this.error = '获取题解详情失败: ' + (error.message || '未知错误');
      } finally {
        this.loading = false;
      }
    },
    
    // 获取题目信息
    async fetchQuestionInfo() {
      if (!this.form.question_id) {
        this.form.question_name = '';
        return;
      }

      this.fetching = true;
      try {
        console.log("获取题目信息，ID:", this.form.question_id);
        const response = await getQuestionDetail(this.form.question_id);
        console.log("题目详情响应:", JSON.stringify(response));
        
        // 处理可能的响应结构
        let questionData = response;
        
        if (response.data) {
          if (response.data.code === 200) {
            questionData = response.data.data;
          } else {
            questionData = response.data;
          }
        }
        
        // 尝试所有可能的字段名
        this.form.question_name = 
          questionData.name || 
          questionData.question_name || 
          '';
        
        console.log("设置题目名称:", this.form.question_name);
      } catch (error) {
        console.error('获取题目信息失败:', error);
        ElMessage.error('获取题目信息失败: ' + (error.message || '未知错误'));
        this.form.question_name = '';
      } finally {
        this.fetching = false;
      }
    },
    
    // 跳转到题目页面
    goToProblem() {
      if (this.form.question_id) {
        this.$router.push(`/problems/${this.form.question_id}`);
      }
    },
    
    // 初始化 MathJax
    initMathJax() {
      if (this.mathJaxLoaded || typeof MathJax !== 'undefined') {
        this.mathJaxLoaded = true;
        return;
      }
      
      // 配置MathJax
      window.MathJax = {
        tex: {
          inlineMath: [['$', '$'], ['\\(', '\\)']],
          displayMath: [['$$', '$$'], ['\\[', '\\]']],
          processEscapes: true,
          tags: 'ams'
        },
        options: {
          enableMenu: false,
          skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code'],
          processHtmlClass: 'markdown-content'
        },
        svg: {
          fontCache: 'global'
        },
        startup: {
          ready: () => {
            window.MathJax.startup.defaultReady();
            this.mathJaxLoaded = true;
            
            // 如果内容已加载并且在预览标签，立即渲染
            if (this.form.content_text && this.activeTab === 'preview') {
              this.$nextTick(() => this.renderMathJax());
            }
          }
        }
      };
      
      // 加载MathJax脚本
      const script = document.createElement('script');
      script.src = 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js';
      script.async = true;
      
      script.onload = () => {
        console.log('MathJax脚本加载完成');
      };
      
      script.onerror = () => {
        console.error('MathJax脚本加载失败，尝试备用CDN');
        const backupScript = document.createElement('script');
        backupScript.src = 'https://cdnjs.cloudflare.com/ajax/libs/mathjax/3.2.0/es5/tex-svg.js';
        backupScript.async = true;
        document.head.appendChild(backupScript);
      };
      
      document.head.appendChild(script);
    },
    
    // 渲染MathJax公式
    renderMathJax() {
      if (typeof MathJax !== 'undefined' && MathJax.typesetPromise) {
        // 获取预览区域
        const previewArea = this.$refs.markdownPreview;
        if (!previewArea) return;
        
        // 执行渲染
        MathJax.typesetPromise([previewArea]).catch(err => {
          console.error('MathJax公式渲染错误:', err);
        });
      }
    },
    
    // 验证表单
    validateForm() {
      if (!this.form.question_id) {
        ElMessage.error('请输入题目ID');
        return false;
      }
      if (!this.form.language) {
        ElMessage.error('请选择编程语言');
        return false;
      }
      if (!this.form.content_text) {
        ElMessage.error('请输入题解内容');
        return false;
      }
      return true;
    },
    
    // 提交表单 - 更新现有题解
    async handleSubmit() {
      if (!this.validateForm()) return;
      
      this.submitting = true;
      
      try {
        // 构建更新数据
        const updateData = {
          question_id: this.form.question_id,
          language: this.form.language,
          content_text: this.form.content_text,
          is_draft: this.form.is_draft
        };
        
        console.log("准备更新题解，ID:", this.solutionId, "数据:", updateData);
        
        // 调用更新API，更新现有题解
        const response = await updateSolution(this.solutionId, updateData);
        console.log("更新成功，响应:", response);
        
        ElMessage({
          type: 'success',
          message: '题解更新成功'
        });
        if(this.form.is_draft) {
          this.$router.push(`/${this.solutionId}/drafts`);
        } else {
          this.$router.push(`/${this.solutionId}/solutions`);
        }
        
        // 重新获取更新后的数据
        this.fetchSolutionDetail();
      } catch (error) {
        console.error('更新题解失败:', error);
        ElMessage({
          type: 'error',
          message: error.response?.data?.message || error.message || '更新失败: 未知错误'
        });
      } finally {
        this.submitting = false;
      }
    },
    
    // 重置表单到原始状态
    handleReset() {
      if (!this.originalSolution) return;
      
      // 重置为原始数据
      this.form = {
        question_id: this.originalSolution.question_id || '',
        question_name: this.originalSolution.question_name || '',
        language: this.originalSolution.language || '',
        content_text: this.originalSolution.content_text || this.originalSolution.content || '',
        is_draft: !!this.originalSolution.is_draft
      };
      
      ElMessage({
        type: 'info',
        message: '已重置为原始数据'
      });
    },
    
    // 删除按钮处理
    handleDelete() {
      this.deleteDialogVisible = true;
    },
    
    // 确认删除现有题解
    async confirmDelete() {
      this.processing = true;
      try {
        console.log("准备删除题解，ID:", this.solutionId);
        
        // 调用删除API
        const response = await request({
          url: '/api/solution/delete/',
          method: 'post',
          data: { id: this.solutionId }
        });
        
        console.log("删除成功，响应:", response);
        this.deleteDialogVisible = false;
        
        ElMessage({
          type: 'success',
          message: response.message || '题解删除成功'
        });
        
        // 跳转到题解列表页
        this.$router.push('/solutions');
      } catch (error) {
        console.error('删除题解失败:', error);
        
        // 尝试从错误对象中获取错误信息
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
    }
  }
};
</script>

<style scoped>
.solution-update-view {
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

.w-100 {
  width: 100%;
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