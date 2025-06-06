import request from './request'

export function login(data) {
  return request({
    url: '/auth/login/',
    method: 'post',
    data
  })
}

export function register(data) {
  return request({
    url: '/auth/register/',
    method: 'post',
    data
  })
}
