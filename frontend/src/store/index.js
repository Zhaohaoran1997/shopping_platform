import { createStore } from 'vuex'

export default createStore({
  state: {
    auth: {
      isLoggedIn: false,
      user: null,
      token: null
    }
  },
  mutations: {
    SET_AUTH(state, { isLoggedIn, user, token }) {
      state.auth.isLoggedIn = isLoggedIn
      state.auth.user = user
      state.auth.token = token
    },
    CLEAR_AUTH(state) {
      state.auth.isLoggedIn = false
      state.auth.user = null
      state.auth.token = null
    }
  },
  actions: {
    login({ commit }, { user, token }) {
      commit('SET_AUTH', { isLoggedIn: true, user, token })
      localStorage.setItem('token', token)
    },
    logout({ commit }) {
      commit('CLEAR_AUTH')
      localStorage.removeItem('token')
    },
    initializeAuth({ commit }) {
      const token = localStorage.getItem('token')
      if (token) {
        // TODO: 验证 token 并获取用户信息
        commit('SET_AUTH', { isLoggedIn: true, user: null, token })
      }
    }
  },
  getters: {
    isLoggedIn: state => state.auth.isLoggedIn,
    currentUser: state => state.auth.user,
    token: state => state.auth.token
  }
}) 