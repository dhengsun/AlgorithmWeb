import request from './request'

export function getActivityData() {
  return request({
    url: '/api/activity/',
    method: 'get'
  })
}
