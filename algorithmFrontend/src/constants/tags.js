// LeetCode相关标签
export const LeetcodeTags = [
    "Shell",
    "二分查找",
    "二叉搜索树",
    "二叉树",
    "交互",
    "位运算",
    "分治",
    "前缀和",
    "单向链表",
    "单调栈",
    "单调队列",
    "双向链表",
    "双指针",
    "双连通分量",
    "后缀数组",
    "哈希函数",
    "哈希表",
    "图",
    "基数排序",
    "堆（优先队列）",
    "字典树",
    "字符串",
    "字符串匹配",
    "归并排序",
    "快速选择",
    "扫描线",
    "拒绝采样",
    "拓扑排序",
    "排序",
    "数论",
    "数学",
    "数据库",
    "数据流",
    "数组",
    "最小生成树",
    "最短路",
    "有序集合",
    "栈",
    "树",
    "树状数组",
    "欧拉回路",
    "概率与统计",
    "模拟",
    "滑动窗口",
    "滚动哈希",
    "深度优先搜索",
    "状态压缩",
    "矩阵",
    "线段树",
    "组合数学",
    "脑筋急转弯",
    "计数",
    "计数排序",
    "设计",
    "贪心",
    "迭代器",
    "递归",
    "链表",
    "队列",
    "随机化",
    "集合",
    "几何",
    "动态规划",
    "博弈",
    "并查集",
    "广度优先搜索",
    "强连通分量",
    "桶排序",
    "水塘抽样",
    "记忆化搜索",
    "回溯",
    "多线程",
    "枚举"
]


// 洛谷难度等级
export const LuoguDifficulties = [
    '入门', '普及-', '普及/提高-', '普及+/提高',
    '提高+/省选-', '省选/NOI-', 'NOI/NOI+', 'CTSC'
]

// LeetCode难度等级
export const LeetcodeDifficulties = ['简单', '中等', '困难']

// 处理洛谷API返回的标签数据
export const processLuoguTags = (apiResponse) => {
    const tagsList = [];
    
    // 主要处理 Algorithm 类型的标签，因为这些是算法相关标签
    if (apiResponse.data && apiResponse.data.Algorithm) {
        apiResponse.data.Algorithm.forEach(tag => {
            tagsList.push(tag.name);
        });
    }
    
    return tagsList;
}

// 洛谷标签将通过API动态获取
export let LuoguTags = [];

// 可以提供一个更新标签的方法
export const updateLuoguTags = (apiResponse) => {
    LuoguTags = processLuoguTags(apiResponse);
}
