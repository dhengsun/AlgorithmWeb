import request from './request'

export function getSolutionList(params) {
  return request({
    url: '/api/solutions/',
    method: 'get',
    params
  })
}

export function getSolutionTrashList(params) {
  return request({
    url:'/api/solutions/trash/',
    method: 'get',
    params
  })
}

export function getDraftList(params) {
  return request({
    url: '/api/drafts/',
    method: 'get',
    params
  })
}

export function getDraftTrashList(params) {
  return request({
    url:'/api/drafts/trash/',
    method: 'get',
    params
  })
}

export function getSolutionDetail(id) {
  return request({
    url: `/solutions/${id}/`,
    method: 'get'
  })
}

export function getDraftDetail(id) {
  return request({
    url: `/drafts/${id}/`,
    method: 'get'
  })
}



export function publishSolution(data) {
  return request({
    url: '/api/solution/create/',
    method: 'post',
    data
  })
}

export function saveDraft(data) {
  return request({
    url: '/api/solution/draft/',
    method: 'post',
    data
  })
}

export function updateSolution(id, data) {
  return request({
    url: `/solutions/${id}/update/`,
    method: 'put',
    data
  })
}

export function updateDraft(id, data) {
  return request({
    url: `/drafts/${id}/update/`,
    method: 'put',
    data
  })
}

export function getSolutionCount() {
  return request({
    url: '/api/solutions/count/',
    method: 'get'
  })
}

export function getDraftCount() {
  return request({
    url: '/api/drafts/count/',
    method: 'get'
  })
}

export function deleteSolution() {
  return request({
    url: '/api/solution/delete/',
    method: 'post'
  })
}

export function restoreSolution() {
  return request({
    url: '/api/solution/restore/',
    method: 'post'
  })
}

export function DraftToSolution() {
  return request({
    url:'/api/solution/pub/',
    method: 'post'
  })
}
