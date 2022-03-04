<template>
    <div class="container">
        <div></div>
        <div class="row login">
            <template v-if="!confirmURL">
                <div class="col col-lg-6">
                    <b-alert :show="messageShow" :variant="messageVariant" v-html="messageText" />
                    <b-form id="login" @submit.prevent="submitGalaxyLogin()">
                        <b-card v-if="enable_oidc" no-body class="text-center mb-4">
                            <b-card-header>
                                <p class="mb-0">
                                    <b>Sign in using an Australian University ID</b>
                                    <span class="px-3">
                                        <i
                                            class="fa fa-info-circle"
                                            @click="toggleAafInfo"
                                            style="cursor: pointer;"
                                        />
                                    </span>
                                </p>

                                <div v-if="showAafInfo" class="login-info">
                                    <small>
                                        Sign in with your Australian Institute login to access our premium service, which includes higher data limits, additional compute and exclusive tools.
                                        <a href="https://site.usegalaxy.org.au/about#feature-catalogue" target="_blank">Learn more.</a>
                                        <br>
                                        <b>Is your institution registered?</b>
                                        Check the
                                        <a href="https://site.usegalaxy.org.au/about/aaf-list" target="_blank">list of AAF institutions</a>.
                                        <br>
                                    </small>
                                </div>
                            </b-card-header>

                            <b-card-body>
                                <!-- Hard-coded AAF OIDC login-->
                                <b-button variant="link" class="my-2" @click="submitOIDCLogin('Keycloak')">
                                    <img :src="https://swift.rc.nectar.org.au/v1/AUTH_377/public/Galaxy/AAF_BTN_Sign_in_med_gradient_orange_FIN2020.png" height="45" alt="" />
                                </b-button>
                            </b-card-body>
                        </b-card>

                        <b-card no-body class="text-center">
                            <b-card-header>
                                <p class="mb-0">
                                    <b>Sign in using another ID</b>
                                    <span class="px-3">
                                        <i
                                            class="fa fa-info-circle"
                                            @click="toggleOtherInfo"
                                            style="cursor: pointer;"
                                        />
                                    </span>
                                </p>

                                <div v-if="showOtherInfo" class="login-info">
                                    <small>
                                        Sign in as a public user with any email address and password. You may have reduced access to the service, such as lower data limits and less server resources. Please use an
                                        <a href="https://site.usegalaxy.org.au/list-of-institutions" target="_blank">Australian Institution email</a>,
                                        if possible.
                                        <a href="https://site.usegalaxy.org.au/about#feature-catalogue" target="_blank">Learn more.</a>
                                    </small>
                                </div>
                            </b-card-header>

                            <b-card-body>
                                <div v-if="!showOther">
                                    <b-button class="my-2" name="other" href="#" @click="clickOther">
                                        <img src="/static/images/au/galaxy-black.svg" style="width: auto; height: 26px; margin-right: 10px; padding: 2px;">
                                        Sign in with email
                                    </b-button>
                                </div>

                                <div v-else class="text-left">
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
            showOther: false,
            showOtherInfo: false,
            showAafInfo: false,
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
        clickOther() {
            this.showOther = true;
        },
        toggleAafInfo() {
            this.showAafInfo = !this.showAafInfo;
        },
        toggleOtherInfo() {
            console.log('clickOtherInfo');
            this.showOtherInfo = !this.showOtherInfo;
            console.log(`showOtherInfo = ${this.showOtherInfo}`);
        },
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
        submitOIDCLogin(idp) {
            const rootUrl = getAppRoot();
            axios
                .post(`${rootUrl}authnz/${idp}/login`)
                .then((response) => {
                    if (response.data.redirect_uri) {
                        window.location = response.data.redirect_uri;
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
.login-info {
    margin: .5rem 0;
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
