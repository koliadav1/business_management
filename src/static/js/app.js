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
        profileForm: { id: '', name: '', surname: '', phone_number: '', email: '', current_password: '', password: '' },
        // Команды
        allTeams: [],
        myTeam: null,
        teamMembers: [],
        newTeamName: '', newTeamDesc: '', inviteCode: '', inviteCodeValue: '',
        addMemberEmail: '',
        addMemberRole: 'employee',
        addMemberId: '',
        // Задачи
        myTasks: [], teamTasks: [], newTaskDesc: '', newTaskDeadline: '', newTaskExecutorId: '',
        newCommentText: '',
        secelctedTask: null,
        lastValidStatus: '',
        editTaskForm: { description: '', deadline: '', executor_id: '' },
        // Оценки
        myEvaluations: [], rateTaskId: '', rateValue: 5, rateComment: '', rateableTasks: [],
        // Meetings
        myMeetings: [], teamMeetings: [], newMeetingDesc: '', newMeetingStart: '', newMeetingDuration: 30, newMeetingMembers: [],
        selectedMeeting: null,
        editMeetingForm: {
            description: '',
            start_time: '',
            duration_m: 30,
            new_member_ids: [],
            remove_member_ids: []
        },
        // URL
        apiBase: 'http://localhost:8000',

        async initApp() {
            const saved = localStorage.getItem('access_token');
            if (saved) {
                this.token = saved;
                await this.refreshUser();
                await this.loadInitialData();
            }
            this.$watch('activeTab', (newTab) => {
                if (newTab !== 'tasks') {
                    this.selectedTask = null;
                    this.editTaskForm = { description: '', deadline: '', executor_id: '' };
                    this.newCommentText = '';
                }
                if (newTab !== 'meetings') {
                    this.selectedMeeting = null;
                    this.editMeetingForm = { description: '', start_time: '', duration_m: 30, new_member_ids: [], remove_member_ids: [] };
                }
            });
            this.$watch('rateTaskId', (id) => {
                const item = this.rateableTasks.find(i => String(i.task.id) === String(id));
                if (item && item.evaluation) {
                    this.rateValue = item.evaluation.rating;
                    this.rateComment = item.evaluation.comment;
                } else {
                    this.rateValue = 5;
                    this.rateComment = '';
                }
            });
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
                        id: this.currentUser.id,
                        name: this.currentUser.name || '',
                        surname: this.currentUser.surname || '',
                        phone_number: this.currentUser.phone_number || '',
                        email: this.currentUser.email,
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
            await this.loadMyTasks(); await this.loadTeamTasks();
            await this.loadMyEvaluations();
            await this.loadRateableTasks();
            await this.loadMyMeetings(); await this.loadTeamMeetings();
        },
        // Встречи
        async loadMyMeetings() {
            const res = await this.fetchWithAuth('/meetings/?include_finished=false');
            if (res.ok) this.myMeetings = await res.json();
        },
        async loadTeamMeetings() {
            const res = await this.fetchWithAuth('/meetings/team');
            if (res.ok) this.teamMeetings = await res.json();
        },
        async createMeeting() {
            const body = {
                description: this.newMeetingDesc,
                start_time: new Date(this.newMeetingStart).toISOString(),
                duration_m: parseInt(this.newMeetingDuration),
                member_ids: this.newMeetingMembers.map(Number)
            };
            const res = await this.fetchWithAuth('/meetings/', { method: 'POST', body: JSON.stringify(body) });
            if (res.ok) { alert('Встреча создана'); this.loadMyMeetings(); this.loadTeamMeetings(); }
            else {
                const errorData = await res.json();
                const errorMessage = errorData.detail?.[0]?.msg || 'Ошибка сервера';
                alert(`Ошибка: ${errorMessage}`);
            }
        },
        async openMeetingDetail(meeting) {
            try {
                const res = await this.fetchWithAuth(`/meetings/${meeting.id}`);
                if (res.ok) {
                    this.selectedMeeting = await res.json();
                    this.editMeetingForm = {
                        description: this.selectedMeeting.description || '',
                        start_time: this.selectedMeeting.start_time ? this.formatDateTimeLocal(this.selectedMeeting.start_time) : '',
                        duration_m: this.selectedMeeting.duration_m || 30,
                        new_member_ids: [],
                        remove_member_ids: []
                    };
                } else {
                    error = await res.json()
                    const errorMessage = error.detail?.[0]?.msg || 'Ошибка сервера';
                    alert(`Ошибка: ${errorMessage}`);
                }
            } catch (e) {
                alert('Ошибка: ' + e.message);
            }
        },
        async updateMeeting() {
            const updateData = {};
            if (this.editMeetingForm.description !== this.selectedMeeting.description) {
                updateData.description = this.editMeetingForm.description;
            }
            if (this.editMeetingForm.start_time) {
                const newStart = new Date(this.editMeetingForm.start_time).toISOString();
                if (newStart !== this.selectedMeeting.start_time) {
                    updateData.start_time = newStart;
                }
            }
            if (this.editMeetingForm.duration_m !== this.selectedMeeting.duration_m) {
                updateData.duration_m = parseInt(this.editMeetingForm.duration_m);
            }
            if (this.editMeetingForm.new_member_ids && this.editMeetingForm.new_member_ids.length > 0) {
                const addMembersRes = await this.fetchWithAuth(`/meetings/${this.selectedMeeting.id}/members`, {
                    method: 'POST',
                    body: JSON.stringify({
                        member_ids: this.editMeetingForm.new_member_ids.map(Number)
                    })
                });
                if (!addMembersRes.ok) {
                    const error = await addMembersRes.json();
                    const errorMessage = error.detail?.[0]?.msg || 'Ошибка сервера';
                    alert(`Ошибка: ${errorMessage}`);
                    return;
                }
            }
            if (this.editMeetingForm.remove_member_ids && this.editMeetingForm.remove_member_ids.length > 0) {
                for (const memberId of this.editMeetingForm.remove_member_ids) {
                    const removeRes = await this.fetchWithAuth(`/meetings/${this.selectedMeeting.id}/members`, {
                        method: 'DELETE',
                        body: JSON.stringify({ member_id: parseInt(memberId) })
                    });

                    if (!removeRes.ok) {
                        const error = await removeRes.json();
                        const errorMessage = error.detail?.[0]?.msg || 'Ошибка сервера';
                        alert(`Ошибка: ${errorMessage}`);
                        return;
                    }
                }
                alert('Участники удалены');
            }
            if (Object.keys(updateData).length === 0 && (!this.editMeetingForm.new_member_ids || this.editMeetingForm.new_member_ids.length === 0)) {
                alert('Нет изменений');
                return;
            }
            if (Object.keys(updateData).length > 0) {
                try {
                    const res = await this.fetchWithAuth(`/meetings/${this.selectedMeeting.id}`, {
                        method: 'PATCH',
                        body: JSON.stringify(updateData)
                    });
                    if (res.ok) {
                        alert('Встреча обновлена');
                        await this.openMeetingDetail(this.selectedMeeting);
                        await this.loadMyMeetings();
                        await this.loadTeamMeetings();
                    } else {
                        const error = await res.json();
                        const errorMessage = error.detail?.[0]?.msg || 'Ошибка сервера';
                        alert(`Ошибка: ${errorMessage}`);
                    }
                } catch (e) {
                    alert('Ошибка: ' + e.message);
                }
            } else {
                await this.openMeetingDetail(this.selectedMeeting);
                await this.loadMyMeetings();
                await this.loadTeamMeetings();
            }
        },
        async cancelMeeting() {
            if (!confirm('Отменить эту встречу?')) return;
            try {
                const res = await this.fetchWithAuth(`/meetings/${this.selectedMeeting.id}/cancel`, {
                    method: 'PATCH'
                });
                if (res.ok) {
                    alert('Встреча отменена');
                    await this.openMeetingDetail(this.selectedMeeting);
                    await this.loadMyMeetings();
                    await this.loadTeamMeetings();
                    this.selectedMeeting = null;
                } else {
                    const error = await res.json();
                    const errorMessage = error.detail?.[0]?.msg || 'Ошибка сервера';
                    alert(`Ошибка: ${errorMessage}`);
                }
            } catch (e) {
                alert('Ошибка: ' + e.message);
            }
        },
        cancelEditMeeting() {
            this.editMeetingForm = {
                description: this.selectedMeeting.description || '',
                start_time: this.selectedMeeting.start_time ? this.formatDateTimeLocal(this.selectedMeeting.start_time) : '',
                duration_m: this.selectedMeeting.duration_m || 30,
                new_member_ids: [],
                remove_member_ids: []
            };
        },
        // Оценки
        async loadMyEvaluations() {
            const res = await this.fetchWithAuth('/evaluations/with-tasks?limit=100');
            if (res.ok) this.myEvaluations = (await res.json()).items;
        },
        async loadRateableTasks() {
            if (!this.isAdminOrManager) return;

            try {
                const res = await this.fetchWithAuth('/tasks/done?limit=100');
                if (res.ok) {
                    const data = await res.json();
                    this.rateableTasks = data.items;
                } else {
                    this.rateableTasks = [];
                }
            } catch (e) {
                console.error(e);
                this.rateableTasks = [];
            }
        },
        get isAlreadyRated() {
            const item = this.rateableTasks.find(i => String(i.task?.id) === String(this.rateTaskId));
            return !!item?.evaluation;
        },
        async submitRating() {
            if (!this.rateTaskId) return;

            const res = await this.fetchWithAuth(`/evaluations/rate/${this.rateTaskId}`, {
                method: 'POST',
                body: JSON.stringify({
                    rating: parseInt(this.rateValue),
                    comment: this.rateComment
                })
            });

            if (res.ok) {
                alert('Оценка сохранена');
                await this.loadRateableTasks();
                if (this.loadMyEvaluations) await this.loadMyEvaluations();
            }
        },
        // Задачи
        async createTask() {
            if (!this.newTaskExecutorId) return alert('Выберите исполнителя');
            const res = await this.fetchWithAuth(
                '/tasks/',
                {
                    method: 'POST',
                    body: JSON.stringify(
                        {
                            description: this.newTaskDesc,
                            deadline: new Date(this.newTaskDeadline).toISOString(),
                            executor_id: parseInt(this.newTaskExecutorId)
                        }
                    )
                }
            );
            if (res.ok) { alert('Задача создана'); this.loadMyTasks(); this.loadTeamTasks(); }
        },
        async loadMyTasks() {
            try {
                const res = await this.fetchWithAuth('/tasks/?limit=100');
                if (res.ok) this.myTasks = (await res.json()).items;
            } catch (e) { }
        },
        async loadTeamTasks() {
            if (!this.isAdminOrManager) return;
            try {
                const res = await this.fetchWithAuth('/tasks/team?limit=100');
                if (res.ok) this.teamTasks = (await res.json()).items;
            } catch (e) { }
        },
        async openTaskDetail(task) {
            const res = await this.fetchWithAuth(`/tasks/${task.id}`);
            if (res.ok) {
                const data = await res.json();
                this.selectedTask = data;
                this.lastValidStatus = data.status;
                this.editTaskForm = {
                    description: data.description || '',
                    deadline: data.deadline ? this.formatDateTimeLocal(data.deadline) : '',
                    executor_id: data.executor_id || ''
                };
            }
        },
        async addCommentToTask() {
            if (!this.selectedTask || !this.newCommentText) return;
            await this.fetchWithAuth(
                `/comments/${this.selectedTask.id}`,
                {
                    method: 'POST',
                    body: JSON.stringify({ content: this.newCommentText })
                }
            );
            this.newCommentText = '';
            await this.openTaskDetail(this.selectedTask);
        },
        async updateTaskStatus() {
            const taskId = this.selectedTask.id;
            const newStatus = this.selectedTask.status;
            const res = await this.fetchWithAuth(`/tasks/${taskId}/status`, {
                method: 'PATCH',
                body: JSON.stringify({ status: newStatus })
            });
            if (res.ok) {
                this.lastValidStatus = newStatus;
                const taskInList = this.teamTasks.find(t => t.id === taskId);
                if (taskInList) taskInList.status = newStatus;
            } else {
                const errorData = await res.json();
                const errorMessage = errorData.detail?.[0]?.msg || 'Ошибка сервера';
                alert(`Ошибка: ${errorMessage}`);
                this.selectedTask.status = this.lastValidStatus;
            }
        },
        async updateTask() {
            const updateData = {};
            if (this.editTaskForm.description !== this.selectedTask.description) {
                updateData.description = this.editTaskForm.description;
            }
            if (this.editTaskForm.deadline) {
                const newDeadline = new Date(this.editTaskForm.deadline).toISOString();
                if (newDeadline !== this.selectedTask.deadline) {
                    updateData.deadline = newDeadline;
                }
            }
            if (this.editTaskForm.executor_id && this.editTaskForm.executor_id !== this.selectedTask.executor_id) {
                const execRes = await this.fetchWithAuth(`/tasks/${this.selectedTask.id}/executor`, {
                    method: 'PATCH',
                    body: JSON.stringify({ executor_id: parseInt(this.editTaskForm.executor_id) })
                });
                if (!execRes.ok) {
                    const error = await execRes.json();
                    const errorMessage = error.detail?.[0]?.msg || 'Ошибка сервера';
                    alert(`Ошибка: ${errorMessage}`);
                    return;
                }
            }
            if (Object.keys(updateData).length === 0) {
                return;
            }
            const res = await this.fetchWithAuth(`/tasks/${this.selectedTask.id}`, {
                method: 'PATCH',
                body: JSON.stringify(updateData)
            });
            if (res.ok) {
                await this.openTaskDetail(this.selectedTask);
                await this.loadMyTasks();
                await this.loadTeamTasks();
            } else {
                const error = await res.json();
                const errorMessage = error.detail?.[0]?.msg || 'Ошибка сервера';
                alert(`Ошибка: ${errorMessage}`);
            }
        },
        cancelEditTask() {
            this.editTaskForm = {
                description: this.selectedTask.description || '',
                deadline: this.selectedTask.deadline ? this.formatDateTimeLocal(this.selectedTask.deadline) : '',
                executor_id: this.selectedTask.executor_id || ''
            };
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
        async addMemberById() {
            if (!this.addMemberId) {
                alert('Введите ID пользователя');
                return;
            }
            await this.addMemberToTeam(parseInt(this.addMemberId), this.addMemberRole);
        },
        async addMemberToTeam(userId, role) {
            const isAlreadyInTeam = this.teamMembers.some(m => m.id === userId);
            if (isAlreadyInTeam) {
                alert('Этот пользователь уже в команде');
                return;
            }
            try {
                const res = await this.fetchWithAuth('/teams/my-team/members', {
                    method: 'POST',
                    body: JSON.stringify({
                        user_id: userId,
                        role: role
                    })
                });
                if (res.ok) {
                    alert('Пользователь добавлен в команду');
                    this.addMemberEmail = '';
                    this.addMemberId = '';
                    this.addMemberRole = 'employee';
                    await this.loadMyTeam();
                } else {
                    const error = await res.json();
                    const errorMessage = error.detail?.[0]?.msg || 'Ошибка сервера';
                    alert(`Ошибка: ${errorMessage}`);
                }
            } catch (e) {
                alert('Ошибка: ' + e.message);
            }
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
                    const errorMessage = error.detail?.[0]?.msg || 'Ошибка сервера';
                    alert(`Ошибка: ${errorMessage}`);
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
                    const errorMessage = error.detail?.[0]?.msg || 'Ошибка сервера';
                    alert(`Ошибка: ${errorMessage}`);
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
        get isAdminOrManager() { return this.currentUser && (this.currentUser.role === 'admin' || this.currentUser.role === 'manager'); },
        get canManage() { return this.currentUser && (this.currentUser.role === 'admin' || this.currentUser.role === 'manager'); },
        get isTaskExecutorAdminAuthor() { return this.selectedTask && (this.selectedTask.executor_id === this.currentUser?.id || this.currentUser?.role === 'admin' || this.selectedTask.author_id === this.currentUser?.id); },
        get isTaskAuthorOrAdmin() {
            return this.selectedTask && (this.selectedTask.author_id === this.currentUser?.id || this.currentUser?.role === 'admin');
        },
        get canManageMeeting() {
            if (!this.selectedMeeting) return false;
            if (!this.selectedMeeting.is_active) return false;
            return this.currentUser?.role === 'admin' || this.selectedMeeting.initiator_id === this.currentUser?.id;
        },
        get availableMembersForMeeting() {
            if (!this.selectedMeeting || !this.teamMembers) return this.teamMembers || [];
            const existingMemberIds = this.selectedMeeting.members?.map(m => m.id) || [];
            return (this.teamMembers || []).filter(m => !existingMemberIds.includes(m.id));
        },
        formatDate(d) { if (!d) return ''; return new Date(d).toLocaleString(); },
        formatDateTimeLocal(dateString) {
            if (!dateString) return '';
            const date = new Date(dateString);
            return date.toISOString().slice(0, 16);
        },
    }
}