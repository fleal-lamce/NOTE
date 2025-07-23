import { useEffect, useState } from 'react'
import './styles.css'
import Server from '../../utils/server'
import { usePeriodicCheck, useStartCheck } from '../../utils/functions'
import LineChart from '../../utils/graphs/line'
import RenderMap from '../../utils/graphs/map'
import { Table, TableRow, TableCell } from '../../utils/table'


export default function HomePage(){
    const server    = new Server()
    const lineChart = new LineChart(15, 0, 100)
    const [tempData, setTempData] = useState([{x: 0, y: 0}])
    const [humData, setHumData]   = useState([{x: 0, y: 0}])
    const [locations, setLocations] = useState([{lat: -22.840022757346, lng: -43.22856553642439}])
    const [counter, setCounter] = useState(0)
    const [table, setTable] = useState([])
    
    useStartCheck(handleServer)
    usePeriodicCheck(handleServer, 2500)

    async function importData(){
        const response = await server.post('rows', {'table': 'logs', 'limit': 30})
        
        if(!response || response.status != 'success')
            return
        
        const data = response.data.map(item => ({esp_id: item.esp_id, data: item.data}))
        setTable(data)
    }

    async function handleServer(){
        await server.check()
        
        if(!server.active)
            return

        await importData()
        await updateData('temperature', setTempData)
        await updateData('humidity', setHumData)
        setCounter(prev => prev + 1)
    }

    async function updateData(key, setVar){
        const response = await server.post('graph', {'key': key})
        
        if(!response || response.status != 'success')
            return false

        const data = response.data.reverse() 
        setVar(data.map((val, i) => ({x: i+counter, y: val})))
    }

    function renderTitleRow(){
        return (
            <div className='TitleRow'>
                Monitoramento Remoto
            </div>
        )
    }

    function renderTable(){
        return (
            <Table>
                <TableRow>
                    <TableCell>ID do Dispositivo</TableCell>
                    <TableCell>Empresa</TableCell>
                </TableRow>

                {table.map(item => {
                    return (
                        <TableRow onClick={() => alert(item)}>
                            <TableCell>{item.esp_id}</TableCell>
                            <TableCell>{item.data}</TableCell>
                        </TableRow>
                    )
                })}
            </Table>
        )
    }

    function renderFirstRow(){
        return (    
            <div className='FirstRow'>
                <div className='simplegraph'>
                    <div className='OuterCell'>
                        <div>Temperatura</div>

                        <div className='BackCell'>
                            {lineChart.plot(tempData)}
                        </div>
                    </div>
                </div>

                <div className='simplegraph'>
                    <div className='OuterCell' style={{backgroundColor: 'transparent', 'justifyContent': 'space-between'}}>
                        <div>Dispositivos</div>

                        <div className='BackCell'>
                            <RenderMap data={locations}/>
                        </div>
                    </div>
                </div>

                <div className='simplegraph'>
                    <div className='OuterCell'>
                        <div>Umidade</div>
                    
                        <div className='BackCell'>
                            {lineChart.plot(humData)}
                        </div>
                    </div>
                </div>
            </div>
        )
    }

    function renderSecondRow(){
        return (
            <div className='FirstRow'>
                <div className='simplegraph'>
                    <div className='OuterCell' style={{backgroundColor: 'transparent', 'justifyContent': 'space-between'}}>
                        <div>Temperatura</div>

                        <div className='BackCell'>
                            {renderTable()}
                        </div>
                    </div>
                </div>
            </div>
        )
    }

    return (
        <div className='MainContainer'>
            <div className='CentralBlock'>
                {renderTitleRow()}
                <div style={{height: '2%'}}/>
                
                <div style={{height: '2%'}}/>
                {renderFirstRow()}

                <div style={{height: '5%'}}/>
                {renderSecondRow()}
            </div>
        </div>
    )
}

