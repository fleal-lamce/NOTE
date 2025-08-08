
export default class Server{
    constructor(){
        this.url    = 'http://10.0.0.9:8000/api/'
        this.active = false;
    }
    
    async post(route, data, timeout=5000){
        const path = this.url + route + '/'
        const controller = new AbortController()
        const id = setTimeout(() => controller.abort(), timeout)
        
        const options = {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body:   JSON.stringify(data),
            signal: controller.signal
        }
        
        try{
            const response = await fetch(path, options)
            clearTimeout(id)
            
            if (!response.ok) 
                return null
    
            return await response.json()
        }
        catch (error){
            //alert(error)
            return null
        }
    }

    async get(route, timeout=5000){
        const path = this.url + route + '/'
        const controller = new AbortController();
        const id = setTimeout(() => controller.abort(), timeout);

        const options = {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' },
            signal: controller.signal,
        };

        try{
            const response = await fetch(path, options);
            clearTimeout(id);

            if (!response.ok) 
                return null;

            return await response.json();
        } 
        catch (error){
            //alert(error);
            return null;
        }
    } 

    async check(){
        const response = await this.get('check')
        this.active    = (response != 'null')
        //alert('server state: ' + this.active)
    }
}

