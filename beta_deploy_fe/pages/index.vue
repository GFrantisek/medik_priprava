<template>
  <div class="container">
    <div class="navigation">
      <NuxtLink to="/" class="nav-item">LF UK BA</NuxtLink>
      <NuxtLink to="/" class="nav-item">JLF UK</NuxtLink>
      <NuxtLink to="/" class="nav-item">LF UPJŠ</NuxtLink>
      <NuxtLink to="/" class="nav-item">LF MU</NuxtLink>
      <NuxtLink to="/" class="nav-item">LF UPOL</NuxtLink>
      <NuxtLink to="/" class="nav-item">LF HK</NuxtLink>
      <NuxtLink to="/" class="nav-item">LFP UK</NuxtLink>
      <NuxtLink to="/" class="nav-item">1. LF UK</NuxtLink>
      <NuxtLink to="/" class="nav-item">2. LF UK</NuxtLink>
      <NuxtLink to="/" class="nav-item">3. LF UK</NuxtLink>
      <div>
        <!-- Check if user is authenticated -->
        <div v-if="$auth.loggedIn">
          <!-- Display logout button if user is logged in -->
          <button @click="logout">Logout</button>
        </div>
        <div v-else>
          <!-- Display login and register links if user is not logged in -->
          <nuxt-link to="/auth/login">Login</nuxt-link>
          <nuxt-link to="/auth/register">Register</nuxt-link>
        </div>
      </div>
    </div>

    <div class="page-title">
      LF UK Bratislava
    </div>

    <div class="three-column-layout">
      <div class="text-column">
        <p>- biológia (100 otázok)</p>
        <p>  - chémia (100 otázok)</p>
        <p>  - pri prezenčnej aj pri online forme prijímacej skúšky test trvá 3 hodiny</p>
        <p>   - prijímacia skúška sa koná samostatne na každý študijný program:</p>
        <p>   15. 6. 2024 všeobecné lekárstvo: online, prezenčne v mestách: Bratislava, Nitra, Banská Bystrica, Košice, Prešov</p>
        <p>   16. 6. 2024 zubné lekárstvo: online, prezenčne v mestách: Bratislava, Banská Bystrica, Košice</p>
        <p>  19. 6. 2024 náhradný termín: online, prezenčne v Bratislave</p>
      </div>

      <div class="subjects-column">
        <button class="subject-item" @click="selectSubject('biologia')">
          <img src="~assets/icons/biologia.png" alt="Biologia" class="subject-icon">
          <span>Biologia</span>
        </button>
        <button class="subject-item" @click="selectSubject('chemia')">
          <img src="~assets/icons/chemia.png" alt="Chemia" class="subject-icon">
          <span>Chemia</span>
        </button>
        <button class="subject-item" @click="selectSubject('fyzika')">
          <img src="~assets/icons/fyzika.png" alt="Fyzika" class="subject-icon">
          <span>Fyzika</span>
        </button>
      </div>


      <div class="test-column">
        <div class="test-container">
          <button @click="generateInteractiveTest" class="standard-test-btn">ŠTANDARDNÝ TEST</button>
          <button @click="generateTest">Stiahnuť ako pdf</button>
          <div class="custom-test">
            <div class="custom-test-title">alebo</div>
            <div class="custom-test-inputs">
              <label for="number-of-questions">Počet otázok:</label>
              <input type="number" id="numQuestions" v-model.number="numQuestions" min="1" />
              <label for="number-of-answers">Počet odpovedí (1-8):</label>
              <input type="number" id="numQuestions" v-model.number="numAnswers" min="1" />
              <label for="from-question-id">Od otázky číslo:</label>
              <input type="number" id="startQuestion" v-model.number="startQuestion" min="1" />
              <label for="to-question-id">Po otázku číslo:</label>
              <input type="number" id="endQuestion" v-model.number="endQuestion" min="1" />
              <label for="to-question-id">Výber oblastí:</label>
            </div>
            <div class="custom-categories">
              <div v-for="(category, index) in allCategories" :key="index">
                <input type="checkbox" :id="`category-${index}`" :value="category" v-model="checkedCategories">
                <label :for="`category-${index}`">{{ category }}</label>
              </div>
            </div>

            <button @click="generateInteractiveTest" class="custom-test-btn">VLASTNÝ TEST</button>
            <button @click="generateTest">Stiahnuť ako pdf</button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
export default {
  computed:{
    isAuthenticated(){
      return this.$auth.loggedIn
    },

    user(){
      return this.$auth.user
    }
  },
  data() {
    return {
      numQuestions: 5,
      startQuestion: 1,
      endQuestion: 10,
      numAnswers: 4,
      checkedCategories: [],
      allCategories: [
        'Všeobecné informácie', 'Bunková biológia', 'DNA a RNA', 'Genetika',
        'Virológia a baktérie', 'Rastliny a huby', 'Živočíchy', 'Človek',
        'Ekosystém a Zem', 'Populačné choroby'
      ],

    };
  },
  methods: {
    async logout(){
      try {
        let response = await this.$auth.logout()
        this.$router.replace({name: 'auth-login'})
      } catch (error) {
        console.log(error)
      }
    },
    async generateTest() {
      try {
        const response = await this.$axios({
          //url: 'https://medik-cloud-i4zdozbjjq-lm.a.run.app/generate-pdf/', //deploy old
          //url: 'http://127.0.0.1:8081/generate-pdf/',                                        //localhost
          url: 'https://medik-cloud-deploy-xxtgwkr47a-uc.a.run.app/generate-pdf/',
          method: 'GET',
          responseType: 'blob',
          params: {
            numQuestions: this.numQuestions,
            startQuestion: this.startQuestion,
            endQuestion: this.endQuestion,
            numAnswers: this.numAnswers,
            categories: this.checkedCategories.join(',')
          },
        });

        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', 'tests_package.zip');
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      } catch (error) {
        console.error('Error during PDF generation or download:', error);
      }
    },
    generateInteractiveTest() {
      this.$router.push({
        path: '/interaktivny_test',
        query: {
          numQuestions: this.numQuestions.toString(),
          startQuestion: this.startQuestion.toString(),
          endQuestion: this.endQuestion.toString(),
          numAnswers: this.numAnswers.toString(),
          categories: this.checkedCategories.join(',')
        }
      });
    },
  },

};
</script>

<style scoped>
.container {
  font-family: 'Arial', sans-serif;
  color: #333;
  padding-top: 60px;
}
.custom-font {
  font-family: 'Montserrat', sans-serif;
  letter-spacing: 0.1em;
}

.navigation {
  background-color: #BB99FF;
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100vw;
  box-sizing: border-box;
  margin: 0;
  position: fixed;
  top: 0;
  left: 0;
  z-index: 1000;
}
.nav-item {
  color: #fff;
  text-decoration: none;
  font-weight: bold;
  margin-left: 20px;
}

.login {
  background-color: #B18BFF;
  padding: 10px 20px;
  border-radius: 20px;
}

.page-title {
  text-align: center;
  font-size: 4em;
  color:#99D9D9;
}
.container {
  display: flex;
  flex-direction: column;
  align-items: center;
}


.three-column-layout {
  display: flex;
  width: 100vw;
  align-content: center;
  justify-content: space-between;
}

.text-column {
  flex: 1;
  padding-right: 20px;
  margin-left: 20px;
  text-align: left;
}

.subjects-column {
  flex: 1;
  padding: 0 10px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.subject-item {
  display: flex;
  align-items: center;
  justify-content: start;
  background-color: #f5f5f5;
  border: 1px solid #ddd;
  margin-bottom: 10px;
  cursor: pointer;
  text-decoration: none;
  height: 10vw;
  width: 100%;
  box-sizing: border-box;
}

.subject-icon {
  margin-right: 10px;
  width: 350px;
  height: auto;
}

button.subject-item {
  padding: 10px;
  border: none;
  outline: none;
  background: none;
  width: 100%;
  text-align: left;
  transition: background-color 0.2s;
}

button.subject-item:hover {
  background-color: #eaeaea;
}

.test-column {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
}
.subject-item {
  margin-bottom: 10px;
}

.subject-icon {
  width: 80px;
  height: auto;
}


.test-section {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px 0;
  width: 100%;
}

.test-container {
  text-align: center;
  background-color: #E6FAF8;
  padding: 10px;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  border-radius: 10px;
}

.custom-test-inputs input {
  width: calc(100% - 20px);
  margin: 5px 0;
  padding: 5px;
  border: 1px solid #ccc;
  border-radius: 5px;
}

.standard-test-btn, .custom-test-btn {
  width: calc(100% - 40px);
  padding: 10px 20px;
  margin: 5px 0;
  border: none;
  border-radius: 5px;
  color: white;
  background-color: #005D60;
  cursor: pointer;
}

.custom-test-inputs label {
  display: block;
  text-align: left;
  margin-left: 10px;
  color: #666;
}

.custom-categories{
  text-align: left;
  margin-left: 10px;
  color: #666;
}
.footer {
  background-color: #37AEB2;
  color: #fff;
  text-align: center;
  padding: 10px;
  position: absolute;
  bottom: 0;
  width: 100%;
}

@media (max-width: 768px) {
  .subjects {
    flex-direction: column;
  }

  .navigation {
    flex-direction: column;
  }

  .nav-item:not(.login) {
    margin-bottom: 10px;
  }
}
</style>
