import './styles.css'

export const Table = ({children}) => {
    return (<div className="table">{children}</div>)
}

export const TableCell = ({children, color='white'}) => {
    return (<div className="table-cell" style={{color: color}}>{children}</div>)
}

export const TableRow = ({children, onClick=undefined, id }) => {
    return (<div className="table-row" id={id} onClick={onClick}>{children}</div>)
}

