import axios from 'axios';
const api=axios.create({baseURL:import.meta.env.VITE_API_URL || '',timeout:90000});
export async function sendMessage(payload){const {data}=await api.post('/chat',payload);return data}
