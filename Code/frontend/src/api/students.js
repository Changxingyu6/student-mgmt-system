import request from './request'

export function getStudents(page = 1, limit = 10) {
  return request({
    url: '/students',
    method: 'get',
    params: { page, limit }
  })
}

export function getStudent(id) {
  return request({
    url: `/students/${id}`,
    method: 'get'
  })
}

export function createStudent(data) {
  return request({
    url: '/students',
    method: 'post',
    data
  })
}

export function updateStudent(id, data) {
  return request({
    url: `/students/${id}`,
    method: 'put',
    data
  })
}

export function deleteStudent(id) {
  return request({
    url: `/students/${id}`,
    method: 'delete'
  })
}