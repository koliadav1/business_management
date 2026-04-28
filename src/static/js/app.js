function app() {
    return {
        // Авторизация
        token: null,
        currentUser: null,
        // UI
        activeTab: 'profile',
        loginEmail: '', loginPassword: '',
        regEmail: '', regPassword: '',
        // Профиль
        profileForm: { name: '', surname: '', phone_number: '', email: '', current_password: '', password: '' },
        // Команды
        allTeams: [],
        myTeam: null,
        teamMembers: [],
        newTeamName: '', newTeamDesc: '', inviteCode: '', inviteCodeValue: '',
        // URL
        apiBase: 'http://localhost:8000',

        async initApp() {
            const saved = localStorage.getItem('access_token');
            if (saved) {
                this.token = saved;
                await this.refreshUser();
                await this.loadInitialData();
            }
        },

        async fetchWithAuth(url, options = {}) {
            if (!this.token) throw new Error('No token');
            const headers = { 'Authorization': `Bearer ${this.token}`, 'Content-Type': 'application/json', ...options.headers };
            let res = await fetch(this.apiBase + url, { ...options, headers });
            if (res.status === 401) {
                const refreshed = await this.refreshToken();
                if (refreshed) {
                    headers['Authorization'] = `Bearer ${this.token}`;
                    res = await fetch(this.apiBase + url, { ...options, headers });
                } else { this.logout(); throw new Error('session expired'); }
            }
            return res;
        },

        async refreshToken() {
            try {
                const refresh = localStorage.getItem('refresh_token');
                if (!refresh) return false;
                const res = await fetch(
                    this.apiBase + '/auth/refresh',
                    {
                        method: 'POST',
                        headers: { 'X-Refresh-Token': refresh }
                    }
                );
                if (res.ok) {
                    const data = await res.json();
                    this.token = data.access_token;
                    localStorage.setItem('access_token', data.access_token);
                    return true;
                }
            } catch (e) { }
            return false;
        },

        async refreshUser() {
            try {
                const res = await this.fetchWithAuth('/users/me');
                if (res.ok) {
                    this.currentUser = await res.json();
                    this.profileForm = {
                        name: this.currentUser.name || '',
                        surname: this.currentUser.surname || '',
                        phone_number: this.currentUser.phone_number || '',
                        email: this.currentUser.email || '',
                        current_password: '',
                        password: ''
                    };
                }
            } catch (e) {
                console.warn(e);
            }
        },

        async loadInitialData() {
            await this.loadAllTeams();
            await this.loadMyTeam();
        },

        // Команды
        async loadAllTeams() {
            try {
                const res = await this.fetchWithAuth('/teams/?limit=100');
                if (res.ok) {
                    const data = await res.json();
                    this.allTeams = data.items;
                } else {
                    this.allTeams = [];
                }
            } catch (e) {
                console.error(e);
                this.allTeams = [];
            }
        },

        async loadMyTeam() {
            if (!this.currentUser?.team_id) {
                this.myTeam = null;
                this.teamMembers = [];
                return;
            }
            try {
                const res = await this.fetchWithAuth('/teams/my-team');
                if (res.ok) {
                    this.myTeam = await res.json();
                } else {
                    this.myTeam = null;
                }
            } catch (e) {
                console.error(e);
                this.myTeam = null;
            }
            try {
                const res = await this.fetchWithAuth('/teams/members');
                if (res.ok) {
                    this.teamMembers = await res.json();
                } else {
                    this.teamMembers = [];
                }
            } catch (e) {
                console.error(e);
                this.teamMembers = [];
            }
        },

        async createTeam() {
            const res = await this.fetchWithAuth(
                '/teams/', {
                method: 'POST',
                body: JSON.stringify(
                    { name: this.newTeamName, description: this.newTeamDesc }
                )
            }
            );
            if (res.ok) {
                alert('Команда создана');
                await this.refreshUser();
                await this.loadMyTeam();
            }
        },

        async joinTeamByCode() {
            const res = await this.fetchWithAuth(
                '/teams/join', {
                method: 'POST',
                body: JSON.stringify(
                    { invite_code: this.inviteCode }
                )
            }
            );
            if (res.ok) { alert('Присоединились'); await this.refreshUser(); await this.loadMyTeam(); }
        },

        async quitTeam() {
            if (confirm('Выйти из команды?')) {
                await this.fetchWithAuth('/teams/members/me', { method: 'DELETE' });
                await this.refreshUser();
                await this.loadMyTeam();
            }
        },

        async getInviteCode() {
            const res = await this.fetchWithAuth('/teams/my-team/invite-code');
            if (res.ok) {
                const data = await res.json();
                this.inviteCodeValue = data.invite_code;
            }
        },

        async deleteTeam() {
            if (confirm('Удалить команду навсегда?')) {
                await this.fetchWithAuth('/teams/my-team', { method: 'DELETE' });
                await this.refreshUser();
                await this.loadMyTeam();
            }
        },

        async removeMember(userId) {
            if (!confirm('Удалить этого участника из команды?')) return;
            try {
                const res = await this.fetchWithAuth(`/teams/my-team/members/${userId}`, {
                    method: 'DELETE'
                });
                if (res.ok) {
                    alert('Участник удален');
                    await this.loadMyTeam();
                } else {
                    const error = await res.text();
                    console.error('Delete failed:', res.status, error);
                    alert(`Ошибка ${res.status}: ${error}`);
                }
            } catch (e) {
                console.error('Error removing member:', e);
                alert('Ошибка: ' + e.message);
            }
        },

        async changeMemberRole(uid, newRole) {
            await this.fetchWithAuth(
                `/teams/my-team/members/${uid}/role`,
                { method: 'PATCH', body: JSON.stringify({ role: newRole }) }
            );
            await this.loadMyTeam();
        },

        // Профиль
        async updateProfile() {
            const updateData = {};
            if (this.profileForm.name !== undefined) updateData.name = this.profileForm.name || null;
            if (this.profileForm.surname !== undefined) updateData.surname = this.profileForm.surname || null;
            if (this.profileForm.phone_number !== undefined) updateData.phone_number = this.profileForm.phone_number || null;
            const changingEmail = this.profileForm.email && this.profileForm.email !== this.currentUser?.email;
            const changingPassword = this.profileForm.password && this.profileForm.password.length > 0;
            if (changingEmail) {
                updateData.email = this.profileForm.email;
            }
            if (changingPassword) {
                updateData.password = this.profileForm.password;
            }
            if ((changingEmail || changingPassword) && this.profileForm.current_password) {
                updateData.current_password = this.profileForm.current_password;
            } else if (changingEmail || changingPassword) {
                alert('Для изменения email или пароля укажите текущий пароль');
                return;
            }
            if (Object.keys(updateData).length === 0) {
                alert('Нет данных для обновления');
                return;
            }
            try {
                const res = await this.fetchWithAuth('/users/me', {
                    method: 'PATCH',
                    body: JSON.stringify(updateData)
                });
                if (res.ok) {
                    alert('Профиль обновлен');
                    await this.refreshUser();
                    this.profileForm.current_password = '';
                    this.profileForm.password = '';
                } else {
                    const error = await res.json();
                    alert('Ошибка: ' + JSON.stringify(error.detail || error));
                }
            } catch (e) {
                alert('Ошибка: ' + e.message);
            }
        },

        // Аккаунт
        async deleteAccount() {
            if (!confirm('Удалить аккаунт?')) return;
            const password = prompt('Введите ваш пароль для подтверждения:');
            if (!password) return;
            try {
                const res = await this.fetchWithAuth(`/users/me?password=${encodeURIComponent(password)}`, {
                    method: 'DELETE'
                });
                if (res.ok) {
                    alert('Аккаунт удален');
                    this.logout();
                } else {
                    const error = await res.json();
                    alert('Ошибка: ' + JSON.stringify(error.detail || error));
                }
            } catch (e) {
                alert('Ошибка: ' + e.message);
            }
        },

        logout() {
            localStorage.clear();
            this.token = null;
            this.currentUser = null;
            this.activeTab = 'profile';
            location.reload();
        },

        async login() {
            const fd = new FormData(); fd.append('username', this.loginEmail); fd.append('password', this.loginPassword);
            const res = await fetch(this.apiBase + '/auth/login', { method: 'POST', body: fd });
            if (!res.ok) { alert('Ошибка входа'); return; }
            const data = await res.json();
            this.token = data.access_token;
            localStorage.setItem('access_token', data.access_token);
            localStorage.setItem('refresh_token', data.refresh_token);
            await this.refreshUser();
            await this.loadInitialData();
            this.activeTab = 'profile';
        },

        async register() {
            const res = await fetch(
                this.apiBase + '/auth/register',
                {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(
                        { email: this.regEmail, password: this.regPassword }
                    )
                }
            );
            if (!res.ok) { alert('Ошибка регистрации'); return; }
            alert('Регистрация успешна, теперь войдите');
            this.loginEmail = this.regEmail;
            this.loginPassword = this.regPassword;
            await this.login();
        },

        // Вспомогательное
        tabLabel(t) {
            return {
                profile: 'Профиль',
                teams: 'Команды',
                tasks: 'Задачи',
                meetings: 'Встречи',
                ratings: 'Оценки',
                calendar: 'Календарь'
            }[t];
        },

        get isTeamAdmin() { return this.currentUser?.role === 'admin' && this.currentUser?.team_id; },
    }
}