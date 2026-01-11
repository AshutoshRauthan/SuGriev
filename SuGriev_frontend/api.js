// API Wrapper
const API = {
    /**
     * Submit a new complaint
     * @param {Object} complaintData - The complaint data
     * @returns {Promise<Object>} Response data
     */
    async submitComplaint(complaintData) {
        try {
            const response = await fetch(`${CONFIG.API_BASE_URL}/api/complaint`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(complaintData)
            });

            if (!response.ok) {
                const errorData = await response.json();
                const errorMessage = typeof errorData.detail === 'object'
                    ? JSON.stringify(errorData.detail)
                    : (errorData.detail || 'Failed to submit complaint');
                throw new Error(errorMessage);
            }

            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },

    /**
     * Admin login
     * @param {string} username 
     * @param {string} password 
     * @returns {Promise<Object>} Response data
     */
    async adminLogin(username, password) {
        try {
            const response = await fetch(`${CONFIG.API_BASE_URL}/api/admin/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Login failed');
            }

            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },

    /**
     * Get dashboard statistics
     * @returns {Promise<Object>} Stats data
     */
    async getDashboardStats() {
        try {
            const response = await fetch(`${CONFIG.API_BASE_URL}/api/admin/dashboard/stats`);
            if (!response.ok) throw new Error('Failed to fetch stats');
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },

    /**
     * Get complaints list
     * @param {number} limit - Optional limit
     * @returns {Promise<Array>} List of complaints
     */
    async getComplaints(limit = null) {
        try {
            let url = `${CONFIG.API_BASE_URL}/api/admin/complaints`;
            if (limit) {
                url += `?limit=${limit}`;
            }
            const response = await fetch(url);
            if (!response.ok) throw new Error('Failed to fetch complaints');
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },

    /**
     * Get complaint details
     * @param {string} complaintNumber 
     * @returns {Promise<Object>} Complaint details
     */
    async getComplaintDetails(complaintNumber) {
        try {
            const response = await fetch(`${CONFIG.API_BASE_URL}/api/admin/complaint/${complaintNumber}`);
            if (!response.ok) throw new Error('Failed to fetch complaint details');
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },

    /**
     * Update complaint status
     * @param {string} complaintNumber 
     * @param {string} status 
     * @returns {Promise<Object>} Response data
     */
    async updateComplaintStatus(complaintNumber, status) {
        try {
            const response = await fetch(`${CONFIG.API_BASE_URL}/api/admin/complaint/${complaintNumber}/status`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ status })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to update status');
            }

            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }
};
