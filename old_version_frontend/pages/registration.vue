<template>
  <div class="auth-container">
    <h2>Register</h2>
    <input v-model="email" type="email" placeholder="Email" />
    <input v-model="password" type="password" placeholder="Password" />
    <button @click="register">Register</button>
  </div>
</template>

<script>
export default {
  name: "registration",
  data() {
    return {
      email: '',
      password: '',
    };
  },
  methods: {
    async register() {
      try {
        // Adjust URL/path according to your API
        await this.$axios.$post('https://your-auth-server.com/register', {
          email: this.email,
          password: this.password,
        });
        this.$router.push('/login');
      } catch (error) {
        console.error('Registration error:', error);
      }
    },
  },
}
</script>

<style scoped>

</style>
