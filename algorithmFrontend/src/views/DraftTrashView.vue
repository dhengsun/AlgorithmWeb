<template>
  <div class="solutions-view">
    <AppHeader />
    <main class="page-container">
      <div class="solutions-header">
        <h1>草稿回收站</h1>
        <p class="solutions-subtitle">管理你的解题思路草稿，随时继续编辑</p>
        
        <!-- 搜索和筛选区域 -->
        <div class="filter-container">
          <div class="search-box">
            <el-input
              v-model="searchQuery"
              placeholder="输入题目ID进行搜索"
              prefix-icon="el-icon-search"
              clearable
              @keyup.enter="handleSearch"
            >
              <template #append>
                <el-button @click="handleSearch">搜索</el-button>
              </template>
            </el-input>
          </div>
          
          <div class="language-filter">
            <el-select
              v-model="selectedLanguage"
              placeholder="编程语言筛选"
              clearable
              @change="handleLanguageChange"
            >
              <el-option
                v-for="lang in languageOptions"
                :key="lang.value"
                :label="lang.label"
                :value="lang.value"
              >
                <span class="language-icon" :class="'lang-' + lang.value.toLowerCase()"></span>
                {{ lang.label }}
              </el-option>
            </el-select>
          </div>
        </div>
      </div>
      
      <!-- 内容展示区 -->
      <div class="content-area">
        <div v-if="loading" class="loading-container">
          <el-skeleton :rows="10" animated />
        </div>
        
        <div v-else-if="solutions.length === 0" class="empty-state">
          <div class="empty-icon">
            <i class="el-icon-document"></i>
          </div>
          <h3>暂无草稿</h3>
          <p>{{ getEmptyStateMessage() }}</p>
          <el-button type="primary" @click="resetFilters">清除筛选条件</el-button>
        </div>
        
        <transition-group 
          name="solution-list" 
          tag="div" 
          class="solutions-grid"
          v-else
        >
          <div 
            v-for="solution in solutions" 
            :key="solution.id" 
            class="solution-card"
            @click="viewDraftDetail(solution.id)"
          >
            <div class="solution-card-header">
              <div class="header-left-section">
                <div class="problem-id-highlight">
                  #{{ solution.question_id }}
                </div>
                <div v-if="questionDetails[solution.question_id]?.oj_platform" class="platform-tag">
                  <el-tag 
                    :type="getPlatformTagType(questionDetails[solution.question_id]?.oj_platform)" 
                    size="small"
                  >
                    {{ getPlatformName(questionDetails[solution.question_id]?.oj_platform) }}
                  </el-tag>
                </div>
              </div>
              <div class="language-tag" :class="'lang-bg-' + getNormalizedLanguage(solution.language)">
                {{ getDisplayLanguage(solution.language) }}
              </div>
            </div>
            
            <div class="solution-card-content">
              <h3 class="solution-title" @click.stop="goToProblem(solution.question_id)">
                <span v-if="questionDetails[solution.question_id]">
                  {{ questionDetails[solution.question_id].name || `题目 #${solution.question_id}` }}
                </span>
                <span v-else>
                  <span v-if="detailsLoading[solution.question_id]">加载中...</span>
                  <span v-else>题目 #{{ solution.question_id }}</span>
                </span>
                <i class="el-icon-link"></i>
              </h3>
              
              <!-- 算法标签区域 -->
              <div class="tags-container" v-if="questionDetails[solution.question_id]?.algorithm_tags?.length">
                <div class="tag-container">
                  <el-tag
                    v-for="tag in getFilteredTags(
                      questionDetails[solution.question_id].algorithm_tags,
                      questionDetails[solution.question_id].oj_platform
                    )"
                    :key="tag"
                    :type="getTagType(tag, questionDetails[solution.question_id].oj_platform)"
                    size="small"
                    class="tag-item"
                  >
                    {{ getTagName(tag) }}
                  </el-tag>
                </div>
              </div>
              
              <div class="solution-preview">
                {{ getSolutionPreview(solution.content_text) }}
              </div>
            </div>
            
            <div class="solution-card-footer">
              <div class="solution-meta">
                <span class="solution-date">
                  <i class="el-icon-time"></i>
                  {{ formatDate(solution.updated_at || solution.created_at) }}
                </span>
              </div>
              <el-button size="small" type="text">查看全文</el-button>
            </div>
          </div>
        </transition-group>
        
        <!-- 分页控件 -->
        <div class="pagination-container" v-if="total > 0">
          <el-pagination
            background
            layout="prev, pager, next, jumper"
            :total="total"
            :page-size="pageSize"
            v-model:current-page="currentPage"
            @current-change="handlePageChange"
          ></el-pagination>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import AppHeader from '@/components/AppHeader.vue'
import { getDraftTrashList } from '@/api/solution'
import { getQuestionDetail } from '@/api/question'
import { LeetcodeTags } from '@/constants/tags'
export default {
  name: 'DraftView',
  components: {
    AppHeader
  },
  data() {
    return {
      solutions: [],
      loading: true,
      total: 0,
      currentPage: 1,
      pageSize: 12, // 每页显示的题解数量
      searchQuery: '',
      selectedLanguage: '',
      questionDetails: {}, // 存储题目详细信息
      detailsLoading: {}, // 跟踪各题目详情的加载状态
      
      // 预设语言选项
      languageOptions: [
        { value: 'Python', label: 'Python' },
        { value: 'Java', label: 'Java' },
        { value: 'C++', label: 'C++' },
        { value: 'JavaScript', label: 'JavaScript' },
        { value: 'Go', label: 'Go' },
        { value: 'Rust', label: 'Rust' },
        { value: 'C#', label: 'C#' },
        { value: 'Ruby', label: 'Ruby' },
        { value: 'Swift', label: 'Swift' },
        { value: 'Kotlin', label: 'Kotlin' }
      ],
      
      // 语言名称到API参数的映射
      languageParamMap: {
        'c++': 'cpp',
        'c#': 'csharp'
      },
      
      // 语言API参数到显示名称的映射
      languageDisplayMap: {
        'cpp': 'C++',
        'csharp': 'C#'
      },
      
      // 平台映射
      platformMap: {
        luogu: '洛谷',
        leetcode: 'LeetCode'
      },
      
      // LeetCode标签列表
      leetcodeTags : LeetcodeTags
    }
  },
  created() {
    this.fetchSolutions()
  },
  methods: {
    // 获取题解列表
    async fetchSolutions() {
      this.loading = true
      
      try {
        // 构建查询参数
        const params = {
          page: this.currentPage
        }
        
        // 仅当有值时才添加可选参数
        if (this.searchQuery.trim()) {
          params.question_id = this.searchQuery.trim()
        }
        
        // 处理语言参数，转换为小写并应用映射
        if (this.selectedLanguage) {
          const languageParam = this.selectedLanguage.toLowerCase()
          // 检查是否需要特殊映射（如 c++ -> cpp）
          params.language = this.languageParamMap[languageParam] || languageParam
        }
        
        // 调用API
        const response = await getDraftTrashList(params)
        
        // 检查响应格式
        if (response.data) {
          // 直接使用response.data作为数据源，适应不同的API响应格式
          if (Array.isArray(response.data)) {
            // 如果是数组，表示直接返回了项目列表
            this.solutions = response.data
            this.total = response.data.length
          } else if (response.data.code === 200 && response.data.data) {
            // 如果是带有code的标准格式
            if (Array.isArray(response.data.data)) {
              this.solutions = response.data.data
              this.total = response.data.data.length
            } else if (response.data.data.items) {
              this.solutions = response.data.data.items || []
              this.total = response.data.data.total || this.solutions.length
            } else {
              this.solutions = []
              this.total = 0
            }
          } else {
            // 其他情况，尝试解析各种可能的格式
            this.solutions = response.data.items || response.data.results || response.data.data || []
            this.total = response.data.total || response.data.count || this.solutions.length || 0
          }
        } else {
          this.solutions = []
          this.total = 0
        }
        
        // 获取题目详情
        this.fetchQuestionDetails()
      } catch (error) {
        this.$message.error('获取草稿列表失败: ' + (error.message || '未知错误'))
        
        // 在开发环境下使用模拟数据
        if (process.env.NODE_ENV === 'development') {
          this.useMockData()
        } else {
          this.solutions = []
          this.total = 0
        }
      } finally {
        this.loading = false
      }
    },
    
    // 获取题目详情
    async fetchQuestionDetails() {
      // 获取唯一题目ID列表
      const questionIds = [...new Set(this.solutions.map(solution => solution.question_id))]
      
      // 为每个题目ID获取详情
      for (const id of questionIds) {
        // 避免重复请求
        if (this.questionDetails[id] || this.detailsLoading[id]) {
          continue
        }
        
        // 标记为加载中
        this.detailsLoading[id] = true
        
        try {
          const response = await getQuestionDetail(id)
          
          if (response.data && response.data.code === 200) {
            // 如果返回标准格式
            this.questionDetails[id] = response.data.data
          } else if (response.data) {
            // 处理其他可能的响应格式
            this.questionDetails[id] = response.data
          }
        } catch (error) {
          // 在开发模式下使用模拟数据
          if (process.env.NODE_ENV === 'development') {
            this.questionDetails[id] = {
              id: id,
              name: `模拟题目 #${id}`,
              oj_platform: ['leetcode', 'luogu'][Math.floor(Math.random() * 2)],
              algorithm_tags: ['数组', '动态规划', 'Algorithm_贪心', 'Source_CSP']
            }
          }
        } finally {
          this.detailsLoading[id] = false
        }
      }
    },
    
    // 开发阶段使用模拟数据
    useMockData() {
      this.solutions = [
        {
          id: 1,
          question_id: '101',
          content: '# 解题思路\n\n这道题可以使用动态规划来解决...',
          content_text: '解题思路\n\n这道题可以使用动态规划来解决，我们定义dp[i]表示到达第i个台阶的方法数，则dp[i] = dp[i-1] + dp[i-2]。边界条件是dp[1]=1, dp[2]=2...',
          language: 'Python',
          created_at: '2025-05-01T10:30:00Z',
          updated_at: '2025-05-01T10:30:00Z'
        },
        {
          id: 2,
          question_id: '102',
          content: '# 双指针解法\n\n使用双指针技巧，可以在O(n)时间内解决...',
          content_text: '双指针解法\n\n使用双指针技巧，可以在O(n)时间内解决这个问题。首先初始化左指针left=0和右指针right=n-1，然后向中间移动...',
          language: 'Java',
          created_at: '2025-04-28T15:20:00Z',
          updated_at: '2025-04-29T09:15:00Z'
        },
        {
          id: 3,
          question_id: '103',
          content: '# 二分查找\n\n对于有序数组，二分查找是最优选择...',
          content_text: '二分查找\n\n对于有序数组，二分查找是最优选择。时间复杂度为O(log n)，远优于线性搜索...',
          language: 'C++',
          created_at: '2025-04-25T20:10:00Z',
          updated_at: '2025-04-25T20:10:00Z'
        }
      ]
      this.total = this.solutions.length
      
      // 在开发环境中添加模拟的题目详情
      this.questionDetails = {
        '101': {
          id: '101',
          name: '爬楼梯',
          difficulty: '简单',
          oj_platform: 'leetcode',
          algorithm_tags: ['动态规划', '数学', '记忆化']
        },
        '102': {
          id: '102',
          name: '两数之和',
          difficulty: '简单',
          oj_platform: 'leetcode',
          algorithm_tags: ['数组', '哈希表']
        },
        '103': {
          id: '103',
          name: '二分查找',
          difficulty: '普及-',
          oj_platform: 'luogu',
          algorithm_tags: ['Algorithm_二分查找', 'Source_CSP', 'Region_中国']
        }
      }
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
    
    // 获取题解预览文本
    getSolutionPreview(content) {
      if (!content) return '无预览内容'
      
      // 移除Markdown标记，限制长度
      const plainText = content
        .replace(/#{1,6}\s/g, '')
        .replace(/\*\*|\*|~~|`|>/g, '')
      
      return plainText.length > 100 
        ? plainText.substring(0, 100) + '...' 
        : plainText
    },
    
    // 格式化日期
    formatDate(dateString) {
      if (!dateString) return '未知时间'
      
      const date = new Date(dateString)
      return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
    },
    
    // 处理页面变化
    handlePageChange(page) {
      this.currentPage = page
      this.fetchSolutions()
      // 滚动到页面顶部
      window.scrollTo(0, 0)
    },
    
    // 处理搜索
    handleSearch() {
      this.currentPage = 1 // 重置到第一页
      this.fetchSolutions()
    },
    
    // 处理语言筛选变化
    handleLanguageChange() {
      this.currentPage = 1 // 重置到第一页
      this.fetchSolutions()
    },
    
    // 重置所有筛选条件
    resetFilters() {
      this.searchQuery = ''
      this.selectedLanguage = ''
      this.currentPage = 1
      this.fetchSolutions()
    },
    
    // 获取空状态消息
    getEmptyStateMessage() {
      if (this.searchQuery && this.selectedLanguage) {
        return `没有找到关于题目 #${this.searchQuery} 的 ${this.selectedLanguage} 语言草稿`
      } else if (this.searchQuery) {
        return `没有找到关于题目 #${this.searchQuery} 的草稿`
      } else if (this.selectedLanguage) {
        return `没有找到使用 ${this.selectedLanguage} 语言的草稿`
      }
      return '暂时没有任何草稿，开始编写你的第一个解题思路吧！'
    },
    
    // 查看草稿详情
    viewDraftDetail(draftId) {
      this.$router.push(`/${draftId}/drafts`)
    },
    
    // 跳转到题目页面
    goToProblem(questionId) {
      this.$router.push(`/${questionId}/problems`)
    },
    
    // 获取平台名称
    getPlatformName(platform) {
      return this.platformMap[platform] || platform
    },
    
    // 平台标签样式
    getPlatformTagType(platform) {
      return {
        luogu: 'success',
        leetcode: 'warning'
      }[platform] || 'info'
    },
    
    // 标签分类过滤
    getFilteredTags(tags, platform) {
      if (!tags) return []
      
      // 默认只显示少量标签，避免卡片过大
      const maxTagsToShow = 3
      
      // LeetCode题目只显示算法标签
      if (platform === 'leetcode') {
        return tags.filter(tag => this.leetcodeTags.includes(tag)).slice(0, maxTagsToShow)
      }
      
      // 洛谷题目优先显示算法标签
      const algorithmTags = tags.filter(tag => tag.startsWith('Algorithm_'))
      if (algorithmTags.length > 0) {
        return algorithmTags.slice(0, maxTagsToShow)
      }
      
      return tags.slice(0, maxTagsToShow)
    },
    
    // 获取标签名称（去掉前缀）
    getTagName(tag) {
      // LeetCode标签已经是纯名称
      if (this.leetcodeTags.includes(tag)) return tag
      
      // 洛谷标签去掉前缀
      return tag.split('_').slice(1).join('_') || tag
    },
    
    // 标签样式分类
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
.solutions-view {
  min-height: 100vh;
  background-color: #f8f9fc;
}

.page-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 30px 20px;
}

.solutions-header {
  margin-bottom: 30px;
  text-align: center;
}

.solutions-header h1 {
  font-size: 2.5rem;
  color: #2c3e50;
  margin-bottom: 0.5rem;
  font-weight: 600;
}

.solutions-subtitle {
  color: #606f7b;
  font-size: 1.1rem;
  margin-bottom: 30px;
}

.filter-container {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 16px;
  margin-bottom: 30px;
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
}

.search-box {
  flex: 1;
  min-width: 280px;
}

.language-filter {
  width: 200px;
}

.content-area {
  position: relative;
  min-height: 400px;
}

.loading-container {
  padding: 20px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.empty-icon {
  font-size: 60px;
  color: #dce0e6;
  margin-bottom: 20px;
}

.empty-state h3 {
  font-size: 20px;
  color: #606266;
  margin-bottom: 10px;
}

.empty-state p {
  color: #909399;
  margin-bottom: 20px;
  max-width: 500px;
}

.solutions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.solution-card {
  background-color: #fff;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.solution-card:hover {
  box-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.09);
  transform: translateY(-3px);
}

.solution-card-header {
  padding: 12px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #f8f9fa;
  border-bottom: 1px solid #f0f0f0;
}

/* Header layout styles */
.header-left-section {
  display: flex;
  align-items: center;
  gap: 8px;
}

.problem-id-highlight {
  background-color: #4caf50;
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: bold;
  font-size: 0.9rem;
  min-width: 40px;
  text-align: center;
}

.platform-tag {
  font-weight: 600;
  color: #606266;
  font-size: 0.9rem;
}

.language-tag {
  padding: 2px 8px;
  border-radius: 4px;
  color: white;
  font-size: 0.8rem;
  font-weight: 500;
}

/* 不同语言的背景色 */
.lang-bg-python {
  background-color: #3776ab;
}

.lang-bg-java {
  background-color: #f89820;
}

.lang-bg-c\+\+ {
  background-color: #00599c;
}

.lang-bg-javascript {
  background-color: #f7df1e;
  color: #000;
}

.lang-bg-go {
  background-color: #00acd7;
}

.lang-bg-rust {
  background-color: #b7410e;
}

.lang-bg-c\# {
  background-color: #68217a;
}

.lang-bg-ruby {
  background-color: #cc342d;
}

.lang-bg-swift {
  background-color: #f05138;
}

.lang-bg-kotlin {
  background-color: #7f52ff;
}

/* 其他语言使用默认颜色 */
[class*="lang-bg-"]:not(
  .lang-bg-python,
  .lang-bg-java,
  .lang-bg-c\+\+,
  .lang-bg-javascript,
  .lang-bg-go,
  .lang-bg-rust,
  .lang-bg-c\#,
  .lang-bg-ruby,
  .lang-bg-swift,
  .lang-bg-kotlin
) {
  background-color: #909399;
}

.solution-card-content {
  padding: 16px;
  flex-grow: 1;
}

.solution-title {
  font-size: 1.1rem;
  margin: 0 0 12px;
  color: #303133;
  display: flex;
  align-items: center;
  line-height: 1.4;
}

.solution-title i {
  margin-left: 6px;
  font-size: 14px;
  opacity: 0.6;
}

.solution-title:hover {
  color: #409eff;
}

.solution-title:hover i {
  opacity: 1;
}

/* 算法标签样式 */
.tags-container {
  margin-bottom: 12px;
}

.tag-container {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tag-item {
  transition: all 0.3s;
  font-size: 0.7rem;
}

.solution-preview {
  color: #606266;
  font-size: 0.95rem;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.solution-card-footer {
  padding: 12px 16px;
  border-top: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.solution-meta {
  color: #909399;
  font-size: 0.85rem;
}

.solution-date i {
  margin-right: 4px;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 40px;
}

/* 语言图标 */
.language-icon {
  display: inline-block;
  width: 16px;
  height: 16px;
  margin-right: 8px;
  background-size: contain;
  background-repeat: no-repeat;
  background-position: center;
  vertical-align: middle;
}

/* 动画效果 */
.solution-list-enter-active, .solution-list-move {
  transition: all 0.5s ease;
}

.solution-list-enter {
  opacity: 0;
  transform: translateY(20px);
}

.solution-list-leave-active {
  position: absolute;
  opacity: 0;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .solutions-header h1 {
    font-size: 2rem;
  }
  
  .filter-container {
    flex-direction: column;
  }
  
  .search-box, .language-filter {
    width: 100%;
  }
  
  .solutions-grid {
    grid-template-columns: 1fr;
  }
}
</style>