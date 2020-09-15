import React from 'react';
import axios from 'axios';
import {isMobile} from 'react-device-detect';
import { getToken, getUser, removeUserSession } from './utils/common';
import { Segment, Image, Feed, Card, Message, Grid, Button, Statistic } from 'semantic-ui-react'
import _ from 'lodash'

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
        expiringcnt: 0
      },
      cardscats: [],
      feed: <Feed>Loading your activities.</Feed>,
      feedcnt: 0
    };
  }

  handlelogout(e) {
    removeUserSession();
    this.props.history.push('/login');
  }

  redirectoproduct(gtin, productname, productimage, productimagelocal, brandname, isedible, isfavourite, categories){
    this.props.history.push({
      pathname: '/products',
      state: { gtin: gtin, productname: productname, productimage: productimage, productimagelocal: productimagelocal, brandname: brandname, isedible: isedible, isfavourite: isfavourite, categoryoptions: categories }
    })
  }

  instantiatefeed(item){
    this.setState({ feedcnt: this.state.feedcnt+1});
    return (
        <Feed.Event key={ item.itemstatus + item.gtin + this.state.feedcnt }>
          <Feed.Label alt={item.productname}>
            <Image
              wrapped src={item.productimagelocal} size='tiny'
              onError={(e)=>{e.target.onerror = null; e.target.src=item.productimage}}
            />
          </Feed.Label>
          <Feed.Content>
            <Feed.Summary>
              {item.itemstatus === 'IN' ? 'added ' : 'consuming '}
              <Feed.User onClick={this.redirectoproduct.bind(this,item.gtin,item.productname, item.productimage, item.productimagelocal, item.brandname, item.isedible, item.isfavourite, item.categories)}>{item.productname}</Feed.User>
              {item.itemstatus === 'IN' ? ' (' + item.itemcount + ' items)' : ''}
              <Feed.Date>{item.dateentry}</Feed.Date>
            </Feed.Summary>
            <Feed.Meta></Feed.Meta>
          </Feed.Content>
        </Feed.Event>
      )
  }

  formatactivityfeed(activities){
    let feed;
    if(activities){
      feed = _.map(activities, (item) => 
        this.instantiatefeed(item)
      );
    }
    else{
      feed = (
        <Feed.Event>
          <Feed.Content>
            <b>No activities.</b>
            <br/>Start tracking items that go in and out of your inventory.
          </Feed.Content>
        </Feed.Event>
      );
    }
    this.setState( { feed: feed});
  }

  getinventoryfeed(){
    console.log('getinventoryfeed');

    axios.get(this.state.apihost + '/inventory/feed',
      {
        headers: {
          "content-type": "application/json",
          "access-token": this.state.token
        }
      }
    )
    .then(response => { 
      if(response.status === 200){
        console.log('getinventoryfeed [' + response.data[0]['message'] + ']');

        this.formatactivityfeed( response.data[0]['results'] );
        this.getinventorybycat();
      }
    })
    .catch(error => {
      if(error.response){
        console.log("getinventoryfeed ["+ error.response.status + ":" + error.response.data[0]['message'] + ']');
      }
      else{
        console.log('getinventoryfeed [server unreachable]');
      }
    });
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

        this.setState({expiringcnt: expiringcnt});
        this.setState({expiredcnt: expiredcnt});
        this.setState({ediblenewcnt: ediblenewcnt});
        this.setState({edibleopenedcnt: edibleopenedcnt});
        this.setState({inediblenewcnt: inediblenewcnt});
        this.setState({inedibleopenedcnt: inedibleopenedcnt});

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

  getinventorybycat(){
    console.log('getinventorybycat');

    axios.get(this.state.apihost + '/inventory/categories',
      {
        headers: {
          "content-type": "application/json",
          "access-token": this.state.token
        }
      }
    )
    .then(response => { 
      if(response.status === 200){
        console.log('getinventorybycat [' + response.data[0]['message'] + ']');

        this.formatinventorybycat( response.data[0]['results'] );
        this.getinventorycount();
      }
    })
    .catch(error => {
      if(error.response){
        console.log("getinventorybycat ["+ error.response.status + ":" + error.response.data[0]['message'] + ']');
      }
      else{
        console.log('getinventorybycat [server unreachable]');
      }
    });
  }

  directtoinventory(isedible,isopened,expirystatus,category){
    const catencoded = encodeURIComponent(category);
    if(isedible >= 0 && isopened >= 0){
      this.props.history.push({
        pathname: '/pantry',
        //search: '?isedible=' + isedible + '&isopened=' + isopened,
        state: { queryisedible: isedible, queryisopened: isopened, queryexpirystatus: expirystatus, querycategory: catencoded }
      })      
    }
    else{
      this.props.history.push({
        pathname: '/tobuy'
      }) 
    }

  }

  componentDidMount() {
    this.getinventoryfeed();
  }

  formatinventorybycat(results){
    const cats = _.map(results, (catobj) => (
        {
          'id': 'id_'+ catobj['name'],
          'number': catobj['count'],
          'label': '' + catobj['name'] + '',
          'isedible':2,'isopened':2,'expirystatus':'all',
          'category': catobj['name']
        }
      ));
    this.setState({cardscats: cats});
  }

  generateinsights(){
    const cardsstats = [
      {
        'id':2,
        'number': this.state.expiringcnt,
        'label': 'expiring food items',
        'isedible':2,'isopened':2,'expirystatus':'expiring',
        'category': 'all'
      },
      {
        'id':3,
        'number': this.state.expiredcnt,
        'label': 'expired food items',
        'isedible':2,'isopened':2,'expirystatus':'expired',
        'category': 'all'
      },
      {
        'id':4,
        'number': this.state.edibleopenedcnt,
        'label': 'opened food items',
        'isedible':1,'isopened':1,'expirystatus':'all',
        'category': 'all'
      },
      {
        'id':5,
        'number': this.state.ediblenewcnt,
        'label': 'new food items',
        'isedible':1,'isopened':0,'expirystatus':'all',
        'category': 'all'
      },
      {
        'id':6,
        'number': this.state.inedibleopenedcnt,
        'label': 'opened non-food items',
        'isedible':0,'isopened':1,'expirystatus':'all',
        'category': 'all'
      },
      {
        'id':7,
        'number': this.state.inediblenewcnt,
        'label': 'new non-food items',
        'isedible':0,'isopened':0,'expirystatus':'all',
        'category': 'all'
      }
    ];

    const cards = cardsstats.concat(this.state.cardscats);

    if(this.state.insightsloaded){
      return cards.map( (card) => (
              <Grid.Column key={card.id} textAlign="center">
                <Card raised key={card.id} fluid onClick={this.directtoinventory.bind(this,card.isedible,card.isopened,card.expirystatus,card.category)}>
                  <Card.Content>
                    <Statistic size="mini">
                      <Statistic.Value>{card.number}</Statistic.Value>
                      <Statistic.Label>{card.label}</Statistic.Label>
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
                header="Generating insights."
                content="Please try again later if it doesn't load."
              />
            </Grid.Column>
          );
    }
  }

  render() {
    return (
      <div
        className={isMobile ? "bodymain mobile" : "bodymain"}
      >
         <Grid columns={2} doubling stackable>
          <Grid.Column textAlign="center">
            <Message size='large'>
              <Message.Header>{this.state.username}'s pantry</Message.Header>
              <p>
                <Button className='kuning button' onClick={this.handlelogout.bind(this)}>LOGOUT</Button>
              </p>
            </Message>
            <Grid columns={2} doubling stackable textAlign='left'>
              {this.generateinsights()}
            </Grid>
          </Grid.Column>
          <Grid.Column textAlign="center">  
            <Message size='large' 
              header="Pantry activities"
            />
            <Segment>
              <Feed>  
                {this.state.feed}    
              </Feed>
            </Segment> 
          </Grid.Column>
        </Grid>
      </div>
    )
  }
}
export default Home;

