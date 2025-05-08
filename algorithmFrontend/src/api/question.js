import request from './request'

export function getQuestionList(data = {}, page = 1) {
  // 确保即使是空对象也会发送请求体
  return request({
    url: '/api/questions/',
    method: 'post',
    params: { page }, // 页码作为URL参数
    data: data, // 其他筛选条件作为请求体
    headers: {
      'Content-Type': 'application/json' // 确保设置正确的内容类型
    }
  })
}

export function getQuestionDetail(id) {
  return request({
    url: `/questions/${id}/`,
    method: 'get'
  })
}


export const searchQuestions = (params) => {
  return request({
    url: '/api/questions/search/',
    method: 'get',
    params
  })
}

export function createQuestion(data) {
  return request({
    url: '/api/questions/create/',
    method: 'post',
    data
  })
}

export function deleteQuestion(data) {
  return request({
    url: '/api/questions/delete/',
    method: 'post',
    data
  })
}

export function updateQuestion(id, data) {
  return request({
    url: `/questions/${id}/update/`,
    method: 'put',
    data
  })
}

export function extractQuestion(data) {
  return request({
    url: '/api/questions/extract/',
    method: 'post',
    data
  })
}

export function getQuestionCount() {
  return request({
    url: '/api/questions/count/',
    method: 'get'
  })
}

export const getAllTags = () => {
  return request({
    url: '/api/tags/',
    method: 'get'
  })
}

export const getTagDetail = (tag_id) => {
  return request({
    url: '/api/tag/',
    method: 'get',
    params: { tag_id }
  })
}

// 回收站接口
export const getQuestionTrashList = (params) => {
  return request({
    url: '/api/questions/trash/',
    method: 'get',
    params
  })
}

export const searchQuestionTrash = (params) => {
  return request({
    url: '/api/questions/trash/search/',
    method: 'get',
    params
  })
}

export function restoreQuestion(data) {
  return request({
    url: '/api/questions/restore/',
    method: 'post',
    data
  })
}