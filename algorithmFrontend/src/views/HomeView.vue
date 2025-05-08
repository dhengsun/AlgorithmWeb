<template>
  <div class="app-container">
    <app-header />
    <div class="content-container">
      <!-- 欢迎区域 -->
      <div class="welcome-container">
        <h1 class="welcome-title">欢迎使用Erix随写录</h1>
        <p class="welcome-subtitle">记录你的编程成长轨迹</p>
      </div>

      <!-- 快速导航卡片 -->
      <div class="quick-actions-container">
        <el-card class="quick-action-card" @click="$router.push('/problems')">
          <div class="action-icon">
            <el-icon><Collection /></el-icon>
          </div>
          <h3>题库</h3>
          <p>浏览所有题目</p>
        </el-card>
        
        <el-card class="quick-action-card" @click="$router.push('/solutions')">
          <div class="action-icon">
            <el-icon><Reading /></el-icon>
          </div>
          <h3>题解</h3>
          <p>查看解题思路</p>
        </el-card>
        
        <el-card class="quick-action-card" @click="$router.push('/drafts')">
          <div class="action-icon">
            <el-icon><Document /></el-icon>
          </div>
          <h3>草稿</h3>
          <p>临时保存草稿</p>
        </el-card>
      </div>

      <!-- 活动日历 -->
      <div class="activity-container">
        <el-card class="activity-card">
          <div class="activity-header">
            <h2>我的编程日历</h2>
            <el-select v-model="timeRange" size="small" style="width: 120px">
              <el-option label="最近半年" value="half_year" />
              <el-option label="最近一年" value="one_year" />
              <el-option label="全部" value="all" />
            </el-select>
          </div>
          
          <div class="heatmap-tabs">
            <div 
              v-for="tab in heatmapTabs" 
              :key="tab.id"
              :class="['heatmap-tab', { active: activeTab === tab.id }]" 
              @click="activeTab = tab.id"
            >
              {{ tab.label }}
            </div>
          </div>
          
          <div class="calendar-container">
            <!-- GitHub风格热力图 -->
            <div class="github-calendar">
              <!-- 月份标签 -->
              <div class="month-labels">
                <div 
                  v-for="(month, index) in monthLabels" 
                  :key="index"
                  class="month-label"
                  :style="{ gridColumnStart: month.columnStart }"
                >
                  {{ month.label }}
                </div>
              </div>
              
              <!-- 日历网格 -->
              <div class="calendar-grid">
                <div 
                  v-for="(day, index) in calendarCells" 
                  :key="index"
                  :class="['calendar-cell', getActivityClass(day)]"
                  :style="{ 
                    gridColumn: day.column, 
                    gridRow: day.row,
                    backgroundColor: day.date ? getActivityColor(day, activeTab) : 'transparent'
                  }"
                >
                  <el-tooltip 
                    v-if="day.date" 
                    effect="dark" 
                    placement="top"
                    :content="formatTooltip(day)"
                  >
                    <div class="cell-content"></div>
                  </el-tooltip>
                </div>
              </div>
              
              <!-- 活动级别图例 -->
              <div class="activity-legend">
                <span class="legend-label">活跃度：</span>
                <ul class="legend-list">
                  <li class="legend-item">
                    <div class="legend-box level-0"></div>
                    <span>无记录</span>
                  </li>
                  <li class="legend-item">
                    <div class="legend-box level-1"></div>
                    <span>1-2条</span>
                  </li>
                  <li class="legend-item">
                    <div class="legend-box level-2"></div>
                    <span>3-5条</span>
                  </li>
                  <li class="legend-item">
                    <div class="legend-box level-3"></div>
                    <span>6-9条</span>
                  </li>
                  <li class="legend-item">
                    <div class="legend-box level-4"></div>
                    <span>10+条</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script>
import AppHeader from '@/components/AppHeader.vue'
import { Collection, Document, Reading} from '@element-plus/icons-vue'
import { getActivityData } from '@/api/activity'

export default {
  name: 'HomeView',
  components: {
    AppHeader,
    Collection,
    Document,
    Reading
  },
  data() {
    return {
      timeRange: 'half_year',
      activityData: {
        questions: {},
        solutions: {},
        drafts: {},
        time_range: {
          start: '',
          end: ''
        }
      },
      activeTab: 'total',
      heatmapTabs: [
        { id: 'total', label: '全部贡献' },
        { id: 'questions', label: '题目' },
        { id: 'solutions', label: '题解' },
        { id: 'drafts', label: '草稿' }
      ],
      colorSchemes: {
        total: ['#ebedf0', '#9be9a8', '#40c463', '#30a14e', '#216e39'],
        questions: ['#ebedf0', '#acd5f2', '#7fa8c9', '#527ba0', '#254e77'],
        solutions: ['#ebedf0', '#fdcfcf', '#fc9494', '#fa6161', '#f73636'],
        drafts: ['#ebedf0', '#fff5a5', '#ffec7a', '#ffe352', '#ffd52a']
      }
    }
  },
  computed: {
    // 计算日历单元格数据
    calendarCells() {
      if (!this.activityData.time_range || !this.activityData.time_range.start) {
        return []
      }
      
      const cells = []
      const startDate = new Date(this.activityData.time_range.start)
      const endDate = new Date(this.activityData.time_range.end)
      
      // 调整到周日开始
      const firstDay = new Date(startDate)
      const dayOfWeek = firstDay.getDay()
      firstDay.setDate(firstDay.getDate() - dayOfWeek)
      
      // 计算总周数
      const totalDays = Math.ceil((endDate - firstDay) / (86400000)) + 1
      const totalWeeks = Math.ceil(totalDays / 7)
      
      let currentDate = new Date(firstDay)
      
      // 生成日历网格
      for (let week = 0; week < totalWeeks; week++) {
        for (let day = 0; day < 7; day++) {
          const dateStr = this.formatDate(currentDate)
          const isInRange = currentDate >= startDate && currentDate <= endDate
          
          const activities = {
            questions: isInRange ? (this.activityData.questions[dateStr] || 0) : 0,
            solutions: isInRange ? (this.activityData.solutions[dateStr] || 0) : 0,
            drafts: isInRange ? (this.activityData.drafts[dateStr] || 0) : 0
          }
          
          // 计算总活动数
          const total = activities.questions + activities.solutions + activities.drafts
          
          cells.push({
            date: isInRange ? dateStr : null,
            day: currentDate.getDate(),
            column: week + 1,
            row: day + 1,
            activities,
            total
          })
          
          currentDate.setDate(currentDate.getDate() + 1)
        }
      }
      
      return cells
    },
    
    // 计算月份标签
    monthLabels() {
      if (!this.calendarCells.length) return []
      
      const months = []
      let currentMonth = ''
      
      this.calendarCells.forEach(cell => {
        if (cell.date) {
          const cellDate = new Date(cell.date)
          const monthKey = `${cellDate.getFullYear()}-${cellDate.getMonth()}`
          
          if (monthKey !== currentMonth) {
            const label = cellDate.toLocaleString('zh-CN', { month: 'short' })
            months.push({
              label,
              columnStart: cell.column
            })
            currentMonth = monthKey
          }
        }
      })
      
      return months
    }
  },
  watch: {
    timeRange() {
      this.fetchActivityData()
    }
  },
  created() {
    this.fetchActivityData()
  },
  methods: {
    // 获取活动数据
    async fetchActivityData() {
      try {
        const response = await getActivityData({ range: this.timeRange })
        this.activityData = response.data
      } catch (error) {
        console.error('获取活动数据失败:', error)
        // 设置默认数据结构，防止界面报错
        this.activityData = {
          questions: {},
          solutions: {},
          drafts: {},
          time_range: {
            start: new Date().toISOString().substring(0, 10),
            end: new Date().toISOString().substring(0, 10)
          }
        }
      }
    },
    
    // 格式化日期为YYYY-MM-DD
    formatDate(date) {
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      return `${year}-${month}-${day}`
    },
    
    // 格式化日期为本地显示格式
    formatLocalDate(dateStr) {
      if (!dateStr) return ''
      const date = new Date(dateStr)
      return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        weekday: 'short'
      })
    },
    
    // 获取活动级别的CSS类
    getActivityClass(day) {
      if (!day.date) return 'empty-cell'
      
      let count = 0
      
      switch (this.activeTab) {
        case 'total':
          count = day.total
          break
        case 'questions':
          count = day.activities.questions
          break
        case 'solutions':
          count = day.activities.solutions
          break
        case 'drafts':
          count = day.activities.drafts
          break
      }
      
      if (count === 0) return 'level-0'
      if (count <= 2) return 'level-1'
      if (count <= 5) return 'level-2'
      if (count <= 9) return 'level-3'
      return 'level-4'
    },
    
    // 获取活动热力图的颜色
    getActivityColor(day, type) {
      if (!day.date) return 'transparent'
      
      let count = 0
      
      switch (type) {
        case 'total':
          count = day.total
          break
        case 'questions':
          count = day.activities.questions
          break
        case 'solutions':
          count = day.activities.solutions
          break
        case 'drafts':
          count = day.activities.drafts
          break
      }
      
      const colors = this.colorSchemes[type]
      
      if (count === 0) return colors[0]
      if (count <= 2) return colors[1]
      if (count <= 5) return colors[2]
      if (count <= 9) return colors[3]
      return colors[4]
    },
    
    // 格式化提示文本
    formatTooltip(day) {
      if (!day.date) return ''
      
      const date = this.formatLocalDate(day.date)
      const lines = [`${date}`]
      
      if (day.activities.questions > 0) {
        lines.push(`题目: ${day.activities.questions} 个`)
      }
      
      if (day.activities.solutions > 0) {
        lines.push(`题解: ${day.activities.solutions} 篇`)
      }
      
      if (day.activities.drafts > 0) {
        lines.push(`草稿: ${day.activities.drafts} 份`)
      }
      
      if (day.total === 0) {
        lines.push('无活动记录')
      } else {
        lines.push(`总计: ${day.total} 个贡献`)
      }
      
      return lines.join('\n')
    }
  }
}
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f5f7fa;
}

.content-container {
  flex: 1;
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

/* 欢迎区域 */
.welcome-container {
  text-align: center;
  margin-bottom: 30px;
  padding: 30px;
  background-color: #ffffff;
  border-radius: 16px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.welcome-container:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  transform: translateY(-5px);
}

.welcome-title {
  font-size: 32px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 16px;
}

.welcome-subtitle {
  font-size: 18px;
  color: #606266;
  margin-bottom: 0;
}

/* 快速导航 */
.quick-actions-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.quick-action-card {
  padding: 25px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.quick-action-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.quick-action-card h3 {
  font-size: 18px;
  color: #303133;
  margin: 15px 0 5px;
}

.quick-action-card p {
  color: #909399;
  font-size: 14px;
  margin: 0;
}

.action-icon {
  font-size: 32px;
  color: #409eff;
  margin: 0 auto;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(64, 158, 255, 0.1);
  border-radius: 50%;
}

/* 活动日历 */
.activity-card {
  padding: 25px;
  border: none;
  border-radius: 16px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.activity-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.activity-header h2 {
  font-size: 20px;
  color: #303133;
  margin: 0;
}

/* 热力图标签页 */
.heatmap-tabs {
  display: flex;
  margin-bottom: 15px;
  border-bottom: 1px solid #e4e7ed;
  overflow-x: auto;
  padding-bottom: 2px;
}

.heatmap-tab {
  padding: 8px 16px;
  cursor: pointer;
  font-size: 14px;
  color: #606266;
  transition: all 0.3s;
  border-bottom: 2px solid transparent;
  white-space: nowrap;
}

.heatmap-tab.active {
  color: #409eff;
  border-bottom-color: #409eff;
  font-weight: 500;
}

.heatmap-tab:hover:not(.active) {
  color: #79bbff;
}

/* 日历容器 */
.calendar-container {
  overflow-x: auto;
  padding-bottom: 10px;
}

/* GitHub风格热力图 */
.github-calendar {
  display: flex;
  flex-direction: column;
  min-width: 730px;
  padding: 10px 0;
  margin: 0 auto; /* 居中显示 */
}

/* 月份标签 */
.month-labels {
  display: grid;
  grid-template-columns: repeat(53, minmax(16px, 1fr));
  margin-bottom: 10px;
  font-size: 12px;
  color: #606266;
}

.month-label {
  text-align: center;
  padding: 0 4px;
}

/* 日历网格 */
.calendar-grid {
  display: grid;
  grid-template-columns: repeat(53, minmax(16px, 1fr));
  grid-template-rows: repeat(7, minmax(16px, 1fr));
  grid-gap: 3px;
  margin: 0 auto; /* 确保网格居中 */
}

.calendar-cell {
  width: 16px;
  height: 16px;
  border-radius: 2px;
  position: relative;
  transition: all 0.2s ease;
}

.calendar-cell:hover {
  transform: scale(1.2);
  z-index: 5;
  border: 1px solid rgba(27, 31, 35, 0.2);
}

.cell-content {
  width: 100%;
  height: 100%;
  cursor: pointer;
}

.empty-cell {
  background-color: transparent !important;
}

/* 活动级别图例 */
.activity-legend {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  margin-top: 15px;
  font-size: 12px;
  color: #606266;
}

.legend-label {
  margin-right: 8px;
}

.legend-list {
  display: flex;
  list-style: none;
  padding: 0;
  margin: 0;
}

.legend-item {
  display: flex;
  align-items: center;
  margin-left: 6px;
}

.legend-box {
  width: 12px;
  height: 12px;
  border-radius: 2px;
  margin-right: 4px;
}

/* 颜色级别 - 会被覆盖，仅用于图例 */
.level-0 { background-color: #ebedf0; }
.level-1 { background-color: #9be9a8; }
.level-2 { background-color: #40c463; }
.level-3 { background-color: #30a14e; }
.level-4 { background-color: #216e39; }

/* 响应式设计 */
@media (max-width: 768px) {
  .welcome-container {
    padding: 20px;
  }
  
  .welcome-title {
    font-size: 24px;
  }
  
  .welcome-subtitle {
    font-size: 16px;
  }
  
  .quick-actions-container {
    grid-template-columns: 1fr;
  }
  
  .activity-card {
    padding: 15px;
  }
  
  .heatmap-tabs {
    padding-bottom: 10px;
  }
  
  .github-calendar {
    min-width: 600px;
  }
}

/* 动画效果 */
.quick-action-card,
.calendar-cell {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
</style>