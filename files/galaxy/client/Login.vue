<template>
    <div class="container">
        <div></div>
        <div class="row login">
            <template v-if="!confirmURL">
                <div class="col col-lg-6">
                    <b-alert :show="messageShow" :variant="messageVariant" v-html="messageText" />
                    <b-form id="login" @submit.prevent="submitGalaxyLogin()">
                        <b-card no-body header="Welcome to Galaxy Australia, please log in">
                            <b-card-body>
                                <div v-if="enable_oidc">
                                    <!-- OIDC login-->
                                    <external-login :login_page="true" />
                                </div>
                                <div>
                                    <!-- Default internal galaxy login -->
                                    <b-form-group label="Public Name or Email Address">
                                        <b-form-input name="login" type="text" v-model="login" />
                                    </b-form-group>
                                    <b-form-group label="Password">
                                        <b-form-input name="password" type="password" v-model="password" />
                                        <b-form-text>
                                            <a @click="reset" href="javascript:void(0)" role="button"
                                                >Forgot password?</a
                                            >
                                        </b-form-text>
                                    </b-form-group>
                                    <b-button name="login" type="submit">Login</b-button>
                                </div>
                            </b-card-body>
                            <b-card-footer>
                                Don't have an account?
                                <span v-if="allowUserCreation">
                                    <a
                                        id="register-toggle"
                                        href="javascript:void(0)"
                                        role="button"
                                        @click.prevent="toggleLogin"
                                        >Register here.</a
                                    >
                                </span>
                                <span v-else>
                                    Registration for this Galaxy instance is disabled. Please contact an administrator
                                    for assistance.
                                </span>
                            </b-card-footer>
                        </b-card>
                    </b-form>

                    <b-modal centered id="duplicateEmail" ref="duplicateEmail" title="Duplicate Email" ok-only>
                        <p>
                            There already exists a user with this email. To associate this external login, you must
                            first be logged in as that existing account.
                        </p>

                        <p>
                            Reminder: Registration and usage of multiple accounts is tracked and such accounts are
                            subject to termination and data deletion. Connect existing account now to avoid possible
                            loss of data.
                        </p>
                        -->
                    </b-modal>
                </div>
            </template>

            <template v-else>
                <confirmation @setRedirect="setRedirect" />
            </template>

            <div v-if="show_welcome_with_login" class="col">
                <b-embed type="iframe" :src="welcome_url" aspect="1by1" />
            </div>
        </div>

        <div class="footer">
            <div class="row">
                <div class="row logo">
                    <a href="https://www.melbournebioinformatics.org.au/" target="_blank">
                        <img src="/static/images/logos/melbourne-bioinformatics.png" />
                    </a>

                    <a href="https://ardc.edu.au/" target="_blank">
                        <img src="/static/images/logos/ardc.png" />
                    </a>

                    <a href="https://bioplatforms.com/" target="_blank">
                        <img src="/static/images/logos/bpa.png" />
                    </a>

                    <a href="https://www.biocommons.org.au/" target="_blank">
                        <img src="/static/images/logos/australian-biocommons.png" />
                    </a>

                    <a href="https://www.qcif.edu.au/" target="_blank">
                        <img src="/static/images/logos/qcif.jpg" />
                    </a>

                    <a href="https://www.dese.gov.au/ncris" target="_blank">
                        <img src="/static/images/logos/ncris.svg" />
                    </a>

                    <a href="https://rcc.uq.edu.au/" target="_blank">
                        <img src="/static/images/logos/uq-2.png" />
                    </a>
                </div>
            </div>

            <p class="text-center">
                The content of this website is licensed under a Creative Commmons Attribute 3.0 Australian License.
                Please review the Galaxy Australia
                <a href="">Terms of Use and Policies.</a>
            </p>
        </div>
    </div>
</template>

<script>
import axios from "axios";
import Vue from "vue";
import BootstrapVue from "bootstrap-vue";
import { getGalaxyInstance } from "app";
import { getAppRoot } from "onload";
import Confirmation from "components/login/Confirmation.vue";
import ExternalLogin from "components/User/ExternalIdentities/ExternalLogin.vue";

Vue.use(BootstrapVue);

export default {
    components: {
        ExternalLogin,
        Confirmation,
    },
    props: {
        show_welcome_with_login: {
            type: Boolean,
            required: false,
        },
        welcome_url: {
            type: String,
            required: false,
        },
    },
    data() {
        const galaxy = getGalaxyInstance();
        return {
            login: null,
            password: null,
            url: null,
            messageText: null,
            messageVariant: null,
            allowUserCreation: galaxy.config.allow_user_creation,
            redirect: galaxy.params.redirect,
            session_csrf_token: galaxy.session_csrf_token,
            enable_oidc: galaxy.config.enable_oidc,
        };
    },
    computed: {
        messageShow() {
            return this.messageText != null;
        },
        confirmURL() {
            var urlParams = new URLSearchParams(window.location.search);
            return urlParams.has("confirm") && urlParams.get("confirm") == "true";
        },
    },
    methods: {
        toggleLogin() {
            if (this.$root.toggleLogin) {
                this.$root.toggleLogin();
            }
        },
        submitGalaxyLogin(method) {
            if (localStorage.getItem("redirect_url")) {
                this.redirect = localStorage.getItem("redirect_url");
            }
            const rootUrl = getAppRoot();
            axios
                .post(`${rootUrl}user/login`, this.$data)
                .then((response) => {
                    if (response.data.message && response.data.status) {
                        alert(response.data.message);
                    }
                    if (response.data.expired_user) {
                        window.location = `${rootUrl}root/login?expired_user=${response.data.expired_user}`;
                    } else if (response.data.redirect) {
                        window.location = encodeURI(response.data.redirect);
                    } else {
                        window.location = `${rootUrl}`;
                    }
                })
                .catch((error) => {
                    this.messageVariant = "danger";
                    const message = error.response.data && error.response.data.err_msg;
                    this.messageText = message || "Login failed for an unknown reason.";
                });
        },
        setRedirect(url) {
            localStorage.setItem("redirect_url", url);
        },
        reset(ev) {
            const rootUrl = getAppRoot();
            ev.preventDefault();
            axios
                .post(`${rootUrl}user/reset_password`, { email: this.login })
                .then((response) => {
                    this.messageVariant = "info";
                    this.messageText = response.data.message;
                })
                .catch((error) => {
                    this.messageVariant = "danger";
                    const message = error.response.data && error.response.data.err_msg;
                    this.messageText = message || "Password reset failed for an unknown reason.";
                });
        },
    },
};
</script>

<style>
  #externalLogin {
    margin-bottom: 2rem;
  }
  #externalLogin hr.my-4 {
    margin: 0.75rem 0;
    border: none;
    border-top: none;
  }
</style>

<style scoped>
.center-panel > div > div.container {
  min-height: 92vh;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
.login {
    margin: 1.5rem;
    width: 100%;
    max-width: 1200px;
    justify-content: center;
}
.card-body {
    overflow: visible;
}
.footer {
    width: 100%;
    display: flex;
    flex-direction: column;
}
.footer .row {
    justify-content: center;
}
.footer .logo {
    border-bottom: 1px solid #ddd;
}
.footer .logo img {
    margin: 1rem;
    height: 50px;
    width: auto;
}
@media only screen and (max-width: 1400px) {
    .footer .logo img {
        height: 40px;
    }
}
@media only screen and (max-width: 1200px) {
    .footer .logo img {
        height: 30px;
    }
}
@media only screen and (max-width: 1000px) {
    .footer .logo img {
        height: 60px;
    }
}
</style>
