import React from 'react';
import axios from 'axios';
import {isMobile} from 'react-device-detect';
import { getToken, getUser, removeUserSession } from './utils/common';
import { Card, Message, Grid, Button, Statistic } from 'semantic-ui-react'

class Home extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      //apihost: 'http://127.0.0.1:88',
      apihost: 'https://inven3s.xyz',
      username: getUser(),
      token: getToken(),
      insightsloaded: false,
      itemcnt : {
        ediblenewcnt: 0,
        edibleopenedcnt: 0,
        inediblenewcnt: 0,
        inedibleopenedcnt: 0,
        expiredcnt: 0,
        expiringcnt: 0,
        shoppinglistcnt: 0,
      }
    };
  }

  handlelogout(e) {
    removeUserSession();
    this.props.history.push('/login');
  }

  getinventorycount(){
    console.log('getinventorycount');

    axios.get(this.state.apihost + '/inventory/insights',
      {
        headers: {
          "content-type": "application/json",
          "access-token": this.state.token
        }
      }
    )
    .then(response => { 
      if(response.status === 200){
        console.log('getinventorycount [' + response.data[0]['message'] + ']');

        const ediblenewcnt = response.data[0]['counts']['ediblenew'];
        const edibleopenedcnt = response.data[0]['counts']['edibleopened'];
        const inediblenewcnt = response.data[0]['counts']['inediblenew'];
        const inedibleopenedcnt = response.data[0]['counts']['inedibleopened'];
        const expiringcnt = response.data[0]['counts']['expiring'];
        const expiredcnt = response.data[0]['counts']['expired'];
        const shoppinglistcnt = response.data[0]['counts']['shoppinglist'];

        this.setState({expiringcnt: expiringcnt});
        this.setState({expiredcnt: expiredcnt});
        this.setState({ediblenewcnt: ediblenewcnt});
        this.setState({edibleopenedcnt: edibleopenedcnt});
        this.setState({inediblenewcnt: inediblenewcnt});
        this.setState({inedibleopenedcnt: inedibleopenedcnt});
        this.setState({shoppinglistcnt: shoppinglistcnt});

        this.setState({insightsloaded: true});
      }
    })
    .catch(error => {
      if(error.response){
        console.log("getinventorycount ["+ error.response.status + ":" + error.response.data[0]['message'] + ']');
      }
      else{
        console.log('getinventorycount [server unreachable]');
      }
    });
  }

  directtoinventory(isedible,isopened,expirystatus){
    if(isedible >= 0 && isopened >= 0){
      this.props.history.push({
        pathname: '/pan3',
        //search: '?isedible=' + isedible + '&isopened=' + isopened,
        state: { queryisedible: isedible, queryisopened: isopened, queryexpirystatus: expirystatus }
      })      
    }
    else{
      this.props.history.push({
        pathname: '/2buy'
      }) 
    }

  }

  componentDidMount() {
    this.getinventorycount();
  }

  generateinsights(){
    const stats = [
     {
        'id':1,
        'number': this.state.shoppinglistcnt,
        'label': 'items in 2Buy',
        'isedible':-1,'isopened':-1,'expirystatus':'all'
      },
      {
        'id':2,
        'number': this.state.expiringcnt,
        'label': 'expiring food items',
        'isedible':2,'isopened':2,'expirystatus':'expiring'
      },
      {
        'id':3,
        'number': this.state.expiredcnt,
        'label': 'expired food items',
        'isedible':2,'isopened':2,'expirystatus':'expired'
      },
      {
        'id':4,
        'number': this.state.edibleopenedcnt,
        'label': 'opened food items',
        'isedible':1,'isopened':1,'expirystatus':'all'
      },
      {
        'id':5,
        'number': this.state.ediblenewcnt,
        'label': 'new food items',
        'isedible':1,'isopened':0,'expirystatus':'all'
      },
      {
        'id':6,
        'number': this.state.inedibleopenedcnt,
        'label': 'opened non-food items',
        'isedible':0,'isopened':1,'expirystatus':'all'
      },
      {
        'id':7,
        'number': this.state.inediblenewcnt,
        'label': 'new non-food items',
        'isedible':0,'isopened':0,'expirystatus':'all'
      }
    ];

    if(this.state.insightsloaded){
      return stats.map( (stat) => (
              <Grid.Column key={stat.id} textAlign="center">
                <Card raised key={stat.id} fluid onClick={this.directtoinventory.bind(this,stat.isedible,stat.isopened,stat.expirystatus)}>
                  <Card.Content>
                    <Statistic size="small">
                      <Statistic.Value>
                      {stat.number}</Statistic.Value>
                      <Statistic.Label>{stat.label}</Statistic.Label>
                    </Statistic>
                  </Card.Content>
                </Card> 
              </Grid.Column>
          ));
    }
    else{
      return (
            <Grid.Column textAlign="center">
              <Message size='tiny'
                header="Generating insights for you"
                content="Please try again later if it doesn't load"
              />
            </Grid.Column>
          )
    }
  }

  render() {
    return (
      <div
        className={isMobile ? "bodymain mobile" : "bodymain"}
      >
         <Grid columns={3} doubling stackable>
          <Grid.Column key="0" textAlign="center">
            <Card raised key="0" fluid>
              <Card.Content>
                <Card.Header>{this.state.username}'s inventory</Card.Header>
              </Card.Content>
              <Card.Content extra>
                <Button className='kuning button fullwidth' onClick={this.handlelogout.bind(this)}>
                LOGOUT</Button>
              </Card.Content>
            </Card> 
          </Grid.Column>
          {this.generateinsights()}
        </Grid>
      </div>
    )
  }
}
export default Home;

