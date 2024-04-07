<template>
  <div class="auth-container">
    <h2>Login</h2>
    <input v-model="email" type="email" placeholder="Email" />
    <input v-model="password" type="password" placeholder="Password" />
    <button @click="login">Login</button>
  </div>
</template>

<script>
export default {
  name: "login",
  data() {
    return {
      email: '',
      password: '',
    };
  },
  methods: {
    async login() {
      try {
        const { token } = await this.$axios.$post('https://your-auth-server.com/login', {
          email: this.email,
          password: this.password,
        });
        localStorage.setItem('authToken', token);
        this.$router.push('/');
      } catch (error) {
        console.error('Login error:', error);
      }
    },
  },
}
</script>

<style scoped>

</style>
