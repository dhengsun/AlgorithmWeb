<template>
  <div class="main-container">
    <!-- 替换原有的filter-card部分 -->
    <div class="filter-card">
      <!-- 搜索框放在最上方 -->
      <div class="search-container">
        <el-input
          v-model="searchQuery"
          placeholder="搜索题目"
          class="search-input"
          clearable
          @clear="handleSearchClear"
          @keyup.enter="handleSearch"
        >
          <template #prepend>
            <el-select 
              v-model="searchType" 
              placeholder="选择类型"
              style="width: 110px"
            >
              <el-option label="题号" value="id" />
              <el-option label="站外ID" value="ext_id" />
              <el-option label="题目名称" value="name" />
            </el-select>
          </template>
          <template #append>
            <el-button 
              type="primary" 
              @click="handleSearch"
              :icon="Search"
            />
          </template>
        </el-input>
      </div>

      <!-- 筛选按钮和模式选择 -->
      <div class="filter-header">
        <el-button type="primary" @click="showFilterDialog" size="small">
          <el-icon><Filter /></el-icon>
          筛选
        </el-button>
        <el-radio-group v-model="filterMode" size="small" style="margin-left: 10px">
          <el-radio-button label="intersection">交集</el-radio-button>
          <el-radio-button label="union">并集</el-radio-button>
        </el-radio-group>
      </div>
      
      <!-- 已选条件展示 -->
      <div class="selected-filters" v-if="hasSelectedFilters">
        <span class="filter-label">已选择：</span>
        <div class="filter-tags">
          <!-- 平台筛选 -->
          <el-tag 
            v-if="selectedPlatform"
            closable
            :type="getPlatformTagType(selectedPlatform)"
            @close="removeFilter('platform')"
          >
            {{ getPlatformName(selectedPlatform) }}
          </el-tag>
          
          <!-- 难度筛选 -->
          <el-tag 
            v-for="diff in selectedDifficulties"
            :key="`diff-${diff}`"
            closable
            :type="getDifficultyTagType({ difficulty: diff, oj_platform: selectedPlatform })"
            @close="removeFilter('difficulty', diff)"
          >
            {{ diff }}
          </el-tag>
          
          <!-- 标签筛选 -->
          <el-tag 
            v-for="tag in selectedTags"
            :key="`tag-${tag}`"
            closable
            :type="getTagType(tag, selectedPlatform)"
            @close="removeFilter('tag', tag)"
          >
            {{ getTagName(tag) }}
          </el-tag>
        </div>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="content-wrapper">
      <!-- 标签展示模式切换（仅对洛谷题目有效） -->
      <div class="tag-mode-switch" v-if="hasLuoguProblems">
        <el-radio-group v-model="tagDisplayMode" size="small">
          <el-radio-button label="algorithm">算法标签</el-radio-button>
          <el-radio-button label="source">来源标签</el-radio-button>
          <el-radio-button label="time">时间标签</el-radio-button>
          <el-radio-button label="region">地区标签</el-radio-button>
          <el-radio-button label="other">其他标签</el-radio-button>
          <el-radio-button label="all">全部标签</el-radio-button>
        </el-radio-group>
      </div>

      <!-- 题目列表表格 -->
      <div class="table-container">
        <el-table 
          :data="problems" 
          style="width: 100%"
          v-loading="loading"
          @row-click="handleRowClick"
        >
          <!-- 题号列 -->
          <el-table-column prop="id" label="题号" width="80" />
          
          <!-- 题目名称列 -->
          <el-table-column label="题目名称" min-width="220">
            <template #default="{row}">
              <span class="problem-title">{{ row.name }}</span>
              <span class="solution-count" v-if="row.solution_count > 0">
                ({{ row.solution_count }}解)
              </span>
            </template>
          </el-table-column>
          
          <!-- 平台列 -->
          <el-table-column label="平台" width="100">
            <template #default="{row}">
              <el-tag :type="getPlatformTagType(row.oj_platform)" size="small">
                {{ getPlatformName(row.oj_platform) }}
              </el-tag>
            </template>
          </el-table-column>

          <!-- 添加题解数列 -->
            <el-table-column prop="solution_count" label="题解" width="80" align="center">
              <template #default="{row}">
                <el-tag v-if="row.solution_count > 0" type="info" size="small">
                  {{ row.solution_count }}
                </el-tag>
                <span v-else>-</span>
              </template>
            </el-table-column>

          <!-- 原题ID列 -->
          <el-table-column label="原题ID" width="120">
            <template #default="{row}">
              <a 
                :href="generateOjLink(row)" 
                target="_blank" 
                class="external-id"
                @click.stop
              >
                {{ row.ext_question_id }}
              </a>
            </template>
          </el-table-column>
          
          <!-- 难度列 -->
          <el-table-column label="难度" width="120">
            <template #default="{row}">
              <el-tag 
                :type="getDifficultyTagType(row)" 
                size="small"
                effect="dark"
              >
                {{ row.difficulty }}
              </el-tag>
            </template>
          </el-table-column>
          
          <!-- 标签列 -->
          <el-table-column label="标签">
            <template #default="{row}">
              <div class="tag-container">
                <el-tag
                  v-for="tag in getFilteredTags(row.algorithm_tags, row.oj_platform)"
                  :key="tag"
                  :type="getTagType(tag, row.oj_platform)"
                  size="small"
                  class="tag-item"
                >
                  {{ getTagName(tag) }}
                </el-tag>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 分页器 -->
      <div class="pagination-wrapper" v-if="totalCount > 0">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="totalCount"
          layout="prev, pager, next"
          @current-change="fetchProblems"
        />
      </div>
    </div>

    <!-- 筛选弹窗 -->
    <el-dialog v-model="filterDialogVisible" title="筛选条件" width="70%">
      <div class="platform-selector">
        <el-radio-group v-model="filterPlatform">
          <el-radio-button label="leetcode">LeetCode</el-radio-button>
          <el-radio-button label="luogu">洛谷</el-radio-button>
        </el-radio-group>
      </div>

      <!-- LeetCode筛选条件 -->
      <div v-if="filterPlatform === 'leetcode'" class="filter-section">
        <h3>难度</h3>
        <div class="tag-group">
          <el-checkbox 
            v-for="diff in LeetcodeDifficulties" 
            :key="diff" 
            :label="diff"
            v-model="tempDifficulties"
            :value="diff"
          />
        </div>

        <h3>算法标签</h3>
        <div class="tag-group">
          <el-checkbox 
            v-for="tag in LeetcodeTags" 
            :key="tag" 
            :label="tag"
            v-model="tempTags"
            :value="tag"
          />
        </div>
      </div>

      <!-- 洛谷筛选条件 -->
      <div v-if="filterPlatform === 'luogu'" class="filter-section">
        <el-tabs type="border-card">
          <el-tab-pane label="难度">
            <div class="tag-group">
              <el-checkbox 
                v-for="diff in LuoguDifficulties" 
                :key="diff" 
                :label="diff"
                v-model="tempDifficulties"
                :value="diff"
              />
            </div>
          </el-tab-pane>

          <el-tab-pane label="算法标签">
            <div class="tag-group">
              <el-checkbox 
                v-for="tag in luoguTags.Algorithm" 
                :key="tag.tag_id" 
                :label="tag.name"
                v-model="tempTags"
                :value="`Algorithm_${tag.name}`"
              />
            </div>
          </el-tab-pane>

          <el-tab-pane label="来源标签">
            <div class="tag-group">
              <el-checkbox 
                v-for="tag in luoguTags.Source" 
                :key="tag.tag_id" 
                :label="tag.name"
                v-model="tempTags"
                :value="`Source_${tag.name}`"
              />
            </div>
          </el-tab-pane>

          <el-tab-pane label="时间标签">
            <div class="tag-group">
              <el-checkbox 
                v-for="tag in luoguTags.Time" 
                :key="tag.tag_id" 
                :label="tag.name"
                v-model="tempTags"
                :value="`Time_${tag.name}`"
              />
            </div>
          </el-tab-pane>

          <el-tab-pane label="地区标签">
            <div class="tag-group">
              <el-checkbox 
                v-for="tag in luoguTags.Region" 
                :key="tag.tag_id" 
                :label="tag.name"
                v-model="tempTags"
                :value="`Region_${tag.name}`"
              />
            </div>
          </el-tab-pane>

          <el-tab-pane label="其他标签">
            <div class="tag-group">
              <el-checkbox 
                v-for="tag in luoguTags.Other" 
                :key="tag.tag_id" 
                :label="tag.name"
                v-model="tempTags"
                :value="`Other_${tag.name}`"
              />
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>

      <template #footer>
        <el-button @click="filterDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="applyFilters">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getAllTags } from '@/api/question'
import { getQuestionTrashList, searchQuestionTrash } from '@/api/question'
import { Filter } from '@element-plus/icons-vue'
import { 
  LeetcodeTags, 
  LuoguDifficulties, 
  LeetcodeDifficulties 
} from '@/constants/tags'
import { Search } from '@element-plus/icons-vue'

const router = useRouter()

// 在setup()中添加以下响应式变量
const searchQuery = ref('')
const searchType = ref('name') // 默认按名称搜索
const isSearching = ref(false)

// 数据状态
const loading = ref(false)
const problems = ref([])
const currentPage = ref(1)
const pageSize = 20
const totalCount = ref(0)
const tagDisplayMode = ref('algorithm')
const filterDialogVisible = ref(false)

// 筛选相关状态（仅用于UI展示）
const selectedPlatform = ref('')
const selectedDifficulties = ref([])
const selectedTags = ref([])

// 临时筛选状态（弹窗中使用）
const filterPlatform = ref('leetcode')
const tempDifficulties = ref([])
const tempTags = ref([])
const filterMode = ref('intersection') // 默认交集
// 洛谷标签
const luoguTags = ref({
  Algorithm: [],
  Source: [],
  Time: [],
  Region: [],
  Other: []
})

// 计算属性
const hasLuoguProblems = computed(() => {
  return problems.value.some(p => p.oj_platform === 'luogu')
})

const hasSelectedFilters = computed(() => {
  return selectedPlatform.value || selectedDifficulties.value.length > 0 || selectedTags.value.length > 0
})

// 加载洛谷标签
const loadLuoguTags = async () => {
  try {
    const res = await getAllTags()
    if (res.data.code === 200) {
      luoguTags.value = res.data.data
    }
  } catch (error) {
    console.error('加载洛谷标签失败:', error)
  }
}

// 显示筛选弹窗
const showFilterDialog = () => {
  // 初始化弹窗中的筛选条件
  filterPlatform.value = selectedPlatform.value || 'leetcode'
  tempDifficulties.value = [...selectedDifficulties.value]
  tempTags.value = [...selectedTags.value]
  filterDialogVisible.value = true
}

// 修改applyFilters函数，添加重新加载数据的逻辑
const applyFilters = () => {
  selectedPlatform.value = filterPlatform.value
  selectedDifficulties.value = [...tempDifficulties.value]
  selectedTags.value = [...tempTags.value]
  filterDialogVisible.value = false
  
  // 重置分页并重新加载数据
  currentPage.value = 1
  fetchProblems()
}

// 修改removeFilter函数，添加重新加载数据的逻辑
const removeFilter = (type, value = null) => {
  switch(type) {
    case 'platform':
      selectedPlatform.value = ''
      break
    case 'difficulty':
      selectedDifficulties.value = selectedDifficulties.value.filter(d => d !== value)
      break
    case 'tag':
      selectedTags.value = selectedTags.value.filter(t => t !== value)
      break
  }
  
  // 重置分页并重新加载数据
  currentPage.value = 1
  fetchProblems()
}

// 平台映射
const PLATFORM_MAP = {
  luogu: '洛谷',
  leetcode: 'LeetCode'
}

// 获取平台名称
const getPlatformName = (platform) => {
  return PLATFORM_MAP[platform] || platform
}

// 平台标签样式
const getPlatformTagType = (platform) => {
  return {
    luogu: 'success',
    leetcode: 'warning'
  }[platform] || 'info'
}

// 难度标签样式
const getDifficultyTagType = (row) => {
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
  return {
    '简单': 'success',
    '中等': 'warning',
    '困难': 'danger'
  }[row.difficulty] || 'info'
}

// 生成OJ题目链接
const generateOjLink = (row) => {
  const baseUrls = {
    luogu: `https://www.luogu.com.cn/problem/${row.ext_question_id}`,
    leetcode: `https://leetcode.cn/problems/${row.ext_question_id}/`
  }
  return baseUrls[row.oj_platform] || '#'
}

// 标签分类过滤
const getFilteredTags = (tags, platform) => {
  if (!tags) return []
  
  // LeetCode题目只显示算法标签
  if (platform === 'leetcode') {
    return tags.filter(tag => LeetcodeTags.includes(tag))
  }
  
  // 洛谷题目根据当前模式过滤
  return tags.filter(tag => {
    if (tagDisplayMode.value === 'all') return true
    
    const prefix = tag.split('_')[0]
    switch(tagDisplayMode.value) {
      case 'algorithm': return prefix === 'Algorithm'
      case 'source': return prefix === 'Source'
      case 'time': return prefix === 'Time'
      case 'region': return prefix === 'Region'
      case 'other': return !['Algorithm', 'Source', 'Time', 'Region'].includes(prefix)
      default: return true
    }
  })
}

// 获取标签名称（去掉前缀）
const getTagName = (tag) => {
  // LeetCode标签已经是纯名称
  if (LeetcodeTags.includes(tag)) return tag
  
  // 洛谷标签去掉前缀
  return tag.split('_').slice(1).join('_') || tag
}

// 标签样式分类
const getTagType = (tag, platform) => {
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

const fetchProblems = async () => {
  try {
    loading.value = true
    
    if (searchQuery.value.trim()) {
      const params = {
        page: currentPage.value,
        page_size: pageSize,
        [searchType.value]: searchQuery.value.trim()
      }
      const res = await searchQuestionTrash(params) // 使用回收站搜索接口
      problems.value = res.data.results
      totalCount.value = res.data.count
      return
    }
    
    const params = {
      page: currentPage.value,
      page_size: pageSize,
      filter_mode: filterMode.value
    }
    
    if (selectedPlatform.value) {
      params.platforms = selectedPlatform.value
    }
    if (selectedDifficulties.value.length > 0) {
      params.difficulties = selectedDifficulties.value.join(',')
    }
    if (selectedTags.value.length > 0) {
      params.algorithm_tags = selectedTags.value.join(',')
    }
    
    const res = await getQuestionTrashList(params) // 使用回收站列表接口
    problems.value = res.data.results
    totalCount.value = res.data.count
    
  } catch (error) {
    console.error('加载回收站题目失败:', error)
  } finally {
    loading.value = false
  }
}


// 初始化加载
onMounted(() => {
  fetchProblems()
  loadLuoguTags()
})

// 跳转到题目详情
const handleRowClick = (row) => {
  router.push(`/problems/${row.id}`)
}


// 修改 handleSearch 方法
const handleSearch = async () => {
  if (!searchQuery.value.trim()) return
  
  try {
    isSearching.value = true
    loading.value = true
    
    const params = {
      page: currentPage.value,
      page_size: pageSize,
      [searchType.value]: searchQuery.value.trim()
    }
    
    const res = await searchQuestionTrash(params) // 使用回收站搜索接口
    problems.value = res.data.results
    totalCount.value = res.data.count
    
    selectedPlatform.value = ''
    selectedDifficulties.value = []
    selectedTags.value = []
    
  } catch (error) {
    console.error('回收站搜索失败:', error)
  } finally {
    loading.value = false
    isSearching.value = false
  }
}

// 清空搜索
const handleSearchClear = () => {
  if (searchQuery.value === '') {
    // 如果已经清空，则恢复原始列表
    fetchProblems()
  }
}


</script>

<style scoped>
.main-container {
  padding-top: 60px;
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%);
}

.filter-card {
  width: 90%;
  max-width: 1200px;
  margin: 0 auto 30px;
  padding: 25px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  backdrop-filter: blur(5px);
  border: 1px solid rgba(0, 0, 0, 0.03);
}

.content-wrapper {
  width: 90%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 25px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.search-container {
  margin-bottom: 20px;
}

.search-input {
  border-radius: 8px;
  overflow: hidden;
}

.filter-header {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

.selected-filters {
  padding: 12px 0;
  border-top: 1px solid rgba(0, 0, 0, 0.05);
}

.filter-label {
  font-size: 14px;
  color: #606266;
  margin-right: 12px;
}

.filter-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.tag-mode-switch {
  margin: 0 0 20px auto;
  padding: 8px 12px;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 6px;
}

.table-container {
  margin: 20px 0;
}

.pagination-wrapper {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid rgba(0, 0, 0, 0.05);
}

.problem-title {
  font-weight: 500;
  color: var(--el-color-primary);
  cursor: pointer;
  transition: all 0.3s;
}

.problem-title:hover {
  color: #409EFF;
  text-decoration: underline;
}

.external-id {
  color: #606266;
  transition: all 0.3s;
}

.external-id:hover {
  color: var(--el-color-primary);
}

.tag-container {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tag-item {
  transition: all 0.3s;
}

.tag-item:hover {
  transform: translateY(-2px);
}

/* 弹窗样式优化 */
:deep(.el-dialog) {
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.95);
}

:deep(.el-dialog__header) {
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.platform-selector {
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.filter-section {
  padding: 0 10px;
}

.tag-group {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

/* 表格优化 */
:deep(.el-table) {
  --el-table-border-color: rgba(0, 0, 0, 0.05);
  --el-table-header-bg-color: rgba(0, 0, 0, 0.02);
}

:deep(.el-table__row) {
  transition: all 0.3s;
}

:deep(.el-table__row:hover) {
  background-color: #f8fafc !important;
  transform: translateY(-1px);
}

:deep(.el-table th.el-table__cell) {
  font-weight: 600;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .filter-card,
  .content-wrapper {
    width: 95%;
    padding: 20px 15px;
  }

  .filter-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .search-container :deep(.el-input-group__prepend) {
    width: 100px;
  }

  .tag-mode-switch {
    margin: 0 auto 20px;
    width: 100%;
  }

  :deep(.el-table) {
    font-size: 14px;
  }
}
</style>