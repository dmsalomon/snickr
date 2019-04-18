import React from 'react';
import ReactDOM from 'react-dom';

class App extends React.Component {
    constructor(props) { super(props);
        this.state = {
            a: '',
            b: '',
            res: 'no result',
        };

        this.change = this.change.bind(this);
        this.submit = this.submit.bind(this);
    }

    change(event) {
        const target = event.target;
        const name = target.name;
        const value = target.value;

        this.setState({
            [name]: value
        });
    }

    submit(event) {
        const a = this.state.a;
        const b = this.state.b;
        const url = `http://localhost:3000/add?a=${a}&b=${b}`
        fetch(url)
            .then(res => res.json())
            .then(
                (json) => {
                    this.setState({
                        res: json.res,
                    });
                },
                (error) => {
                    this.setState({
                        res: 'api error',
                    });
                }
            )
        event.preventDefault();
    }

    render() {
        return (
            <form>
                    My Flask App <br />
                <input
                    type="text"
                    name="a"
                    value={this.state.a}
                    onChange={this.change}
                />
                <input
                    type="text"
                    name="b"
                    value={this.state.b}
                    onChange={this.change}
                />
                <button onClick={this.submit}>
                    Submit
                </button> <br/>
                <textarea value={this.state.res} />
            </form>
        );
    }
}

ReactDOM.render(<App />, document.getElementById('app'));
