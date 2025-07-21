import { useEffect } from 'react'
import './styles.css'
import Server from '../../utils/Server'
import { useStartCheck } from '../../utils/Functions'


export default function HomePage(){
    const server = new Server()
    const {check} = server;

    useStartCheck(importData)
    setInterval(handleServer, 3000)

    async function importData(){
        const response = await server.post('graph', {'key': 'logs'})
        //alert(JSON.stringify(response))
    }

    async function handleServer(){
        await server.check()
    }

    function renderTitleRow(){
        return (
            <div className='TitleRow'>
                Monitoramento Remoto
            </div>
        )
    }

    function renderFirstRow(){
        return (    
            <div className='FirstRow'>
                <div className='simplegraph'>

                </div>

                <div className='simplegraph'>

                </div>

                <div className='simplegraph'>

                </div>
            </div>
        )
    }

    return (
        <div className='MainContainer'>
            <div className='CentralBlock'>
                {renderTitleRow()}
                {renderFirstRow()}
            </div>
        </div>
    )
}

