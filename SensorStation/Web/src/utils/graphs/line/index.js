import { Line } from 'react-chartjs-2';
import 'chart.js/auto';


export default class LineChart{
    constructor(maxPoints=50, min=0, max=50){
        this.maxPoints = maxPoints
        this.min = min
        this.max = max
    }

    plot(data){
        const maxPointX = data.length > 0 ? data[data.length - 1].x : this.maxPoints;
        const minPointX = maxPointX - this.maxPoints;

        if(!data || data.length == 0)
            return (<div/>)

        const graphDataset = {
            datasets: [{
                label: 'Valor em Tempo Real',
                data: data,
                borderColor: 'rgb(75, 192, 192)',
                borderWidth: 2,
                fill: true,
                pointRadius: 0
            }]
        }

        const graphOptions = {
            scales: {
            x: {
                type: 'linear',
                position: 'bottom',
                ticks: {
                maxTicksLimit: 10,
                },
                min: minPointX, // Atualiza o mínimo dinamicamente
                max: maxPointX, // Atualiza o máximo dinamicamente
            },
            y: {
                beginAtZero: true, // Opcional: começa o eixo Y em 0
                min: this.min,         // Define o limite mínimo do eixo Y
                max: this.max,        // Define o limite máximo do eixo Y
            }
            },
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false,
                },
            },
            animation: {
                duration: 0, // Desativa a animação definindo a duração para 0
            },
        };
        
        return (
            <Line style={{backgroundColor: 'white', borderRadius: '5px', padding: '5px'}}
                data={graphDataset} 
                options={graphOptions}
            />
        )
    }
}

