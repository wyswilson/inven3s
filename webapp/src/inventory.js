import React from "react";
import "./index.css";
import axios from 'axios';
import { getToken } from './utils/common';
import { Message, Container, Grid, Dropdown, Modal, Button, Input, Label, Card, Image  } from 'semantic-ui-react'
import { DateInput } from 'semantic-ui-calendar-react';
import _ from 'lodash'

class Inventory extends React.Component {

  constructor(props) {
    super(props)
    this.state = {
      apihost: 'http://127.0.0.1:8989',
      token: getToken(),
      loading: false,
      actionedmsg: '',
      actioned: false,
      modalopen: false,
      defaultimage: 'https://react.semantic-ui.com/images/wireframe/image.png',
      gtin: '',
      productname: '',
      productimage: 'https://react.semantic-ui.com/images/wireframe/image.png',
      brandid:'',
      brandname:'',
      retailerid:'',
      retailername:'',
      inventory:[],
      dateexpiry:'',
      quantity: 1,
      productsuggests: [],
      retailersuggests: [],
      brandsuggests: []
    };
  }

  fetchinventory(){
    axios.get(this.state.apihost + '/inventory?isedible=2&ispartiallyconsumed=2&sortby=productname',
      {
        headers: {
          "content-type": "application/json",
          "access-token": this.state.token
        }
      }
    )
    .then(response => { 
      if(response.status === 200){
        this.setState({ inventory: response.data[0]['results'] });
      }
    })
    .catch(error => {
      if(error.response){
        console.log('(' + error.response.status + ') ' + error.response.data[0]['message']);
      }
      else{
        console.log('server unreachable');
      }
    });
  }

  componentDidMount() {
    this.fetchinventory();
  }

  lookupproduct(event, data){
    const gtinorproduct = data.searchQuery

    if(gtinorproduct.length > 3){
      axios.get(this.state.apihost + '/product/' + gtinorproduct + '?isedible=2',
        {
          headers: {
            "content-type": "application/json",
            "access-token": this.state.token
          }
        }
      )
      .then(response => { 
        if(response.status === 200){
          this.updateproductsuggests(response.data[0]['results']);
        }
      })
      .catch(error => {
        if(error.response){
          console.log('(' + error.response.status + ') ' + error.response.data[0]['message']);
        }
        else{
          console.log('server unreachable');
        }
      });
    }
  }

  lookupretailer(event, data){
    const retailer = data.searchQuery

    if(retailer.length > 3){
      axios.get(this.state.apihost + '/retailer/' + retailer,
        {
          headers: {
            "content-type": "application/json",
            "access-token": this.state.token
          }
        }
      )
      .then(response => { 
        if(response.status === 200){
          this.updateretailersuggests(response.data[0]['results']);
        }
      })
      .catch(error => {
        if(error.response){
          console.log('(' + error.response.status + ') ' + error.response.data[0]['message']);
        }
        else{
          console.log('server unreachable');
        }
      });
    }
  }

  lookupbrand(event, data){
    const brand = data.searchQuery

    if(brand.length > 3){
      axios.get(this.state.apihost + '/brand/' + brand,
        {
          headers: {
            "content-type": "application/json",
            "access-token": this.state.token
          }
        }
      )
      .then(response => { 
        if(response.status === 200){
          this.updatebrandsuggests(response.data[0]['results']);
        }
      })
      .catch(error => {
        if(error.response){
          console.log('(' + error.response.status + ') ' + error.response.data[0]['message']);
        }
        else{
          console.log('server unreachable');
        }
      });
    }
  }

  setinventorymetadata(event, data){
    const field = data.placeholder;
    const value = data.value;
    console.log(field + ':' + value);

    if(field === 'Product name'){
      const array = this.state.productsuggests;
      let selectedarr = array.filter(prod => prod.value.includes(value))[0];

      if(selectedarr){
        const selectedgtin = selectedarr['key'];
        const selectedimg = selectedarr['img'];

        this.setState({ gtin: selectedgtin });
        this.setState({ productname: value });
        this.setState({ productimage: selectedimg });
      }
      else{
        console.log('new product:' + value + ' => handled by addnewproduct')

      }
    }
    else if(field === 'Retailer name'){
      const array = this.state.retailersuggests;
      let selectedarr = array.filter(prod => prod.value.includes(value))[0];
      if(selectedarr){
        const selectedid = selectedarr['key'];
        this.setState({ retailerid: selectedid });
        this.setState({ retailername: value });
      }
      else{
        console.log('new retailer:' + value + ' => handled by addnewretailer')
      }
    }
    else if(field === 'Quantity'){
      this.setState({ quantity: value });
    }
    else if(field === 'Expiry date'){
      this.setState({ dateexpiry: value });
    }
  }
  
  addinventory(gtin){
    this.setState({ actionedmsg: '' });
    this.setState({ actioned: false });
    this.setState({ loading: true });

    axios.post(this.state.apihost + '/inventory', 
      {
        gtin:gtin,
        retailername:this.state.retailername,
        dateexpiry:this.state.dateexpiry,
        quantity:this.state.quantity,
        itemstatus:'IN',
        receiptno:''
      }, 
      {
        headers: {
          'crossDomain': true,
          "content-type": "application/json",
          "access-token": this.state.token
        }
      }
    )
    .then(response => {
      this.setState({ loading: false });
      if(response.status === 200){
        this.setState({ inventory: response.data[0]['results'] });
        this.setState({ actionedmsg: response.data[0]['message'] });
        this.setState({ actioned: true });
        this.setState({ gtin: '' });
        this.setState({ productname: '' });
        this.setState({ productimage: 'https://react.semantic-ui.com/images/wireframe/image.png' });
        this.setState({ retailerid: ''});
        this.setState({ retailername: ''});
        this.setState({ dateexpiry: ''});
        this.setState({ quantity: 1 });
      }
    })
    .catch(error => {
      this.setState({ loading: false });
      if(error.response){
        console.log('(' + error.response.status + ') ' + error.response.data[0]['message']);
        this.setState({ actionedmsg: error.response.data[0]['message'] });        
      }
      else{
        console.log('server unreachable');
        this.setState({ actionedmsg: 'server unreachable' });
      }
    });
  }

  updateproductsuggests(suggestions){
    const updatedsuggest = _.map(suggestions, (item) => (
        {
          key: item.gtin,
          text: item.productname,
          value: item.productname,
          img: item.productimage,
        }
      ));
    console.log(updatedsuggest);
    this.setState({ productsuggests: updatedsuggest });
  }

  updateretailersuggests(suggestions){
    const updatedsuggest = _.map(suggestions, (item) => (
        {
          key: item.retailerid,
          text: item.retailername,
          value: item.retailername,
        }
      ));
    console.log(updatedsuggest);
    this.setState({ retailersuggests: updatedsuggest });
  }

  updatebrandsuggests(suggestions){
    const updatedsuggest = _.map(suggestions, (item) => (
        {
          key: item.brandid,
          text: item.brandname,
          value: item.brandname,
        }
      ));
    console.log(updatedsuggest);
    this.setState({ brandsuggests: updatedsuggest });
  }  

  addnewproduct(event,data){
    console.log('onAddItem for product:' +data.value);
  }

  addnewretailer(event,data){
    console.log('onAddItem for retailer:' + data.value);
  }

  addnewbrand(event,data){
    console.log('onAddItem for brand:' + data.value);
  }

  consumeinventory(gtin){
    console.log(gtin);  
    axios.post(this.state.apihost + '/inventory', 
      {
        gtin:gtin,
        retailername:'',
        dateexpiry:'',
        quantity:0.5,
        itemstatus:'OUT',
        receiptno:''
      }, 
      {
        headers: {
          'crossDomain': true,
          "content-type": "application/json",
          "access-token": this.state.token
        }
      }
    )
    .then(response => { 
      if(response.status === 200){
        console.log(response.data[0]['message']);
        this.setState({ inventory: response.data[0]['results'] });
      }
    })
    .catch(error => {
      if(error.response){
        console.log('(' + error.response.status + ') ' + error.response.data[0]['message']);
        //this.setState({ actionedmsg: error.response.data[0]['message'] });        
      }
      else{
        console.log('server unreachable');
        //this.setState({ actionedmsg: 'server unreachable' });
      }
    });    
  }
  
  openmodal = () => this.setState({ modalopen: true })
  
  closemodal = () => this.setState({ modalopen: false })

  setdefaultimage(event){
    event.target.src = this.state.defaultimage;
  }

  redirectoproduct(gtin){
    console.log('redirect to product/gtin:' + gtin);
    this.props.history.push({
      pathname: '/product',
      state: { gtin: gtin }
    })
  }
  generateitemadditionmsg(){
      if(this.state.actionedmsg !== '' && this.state.actioned){
        return (
          <Message className="fullwidth" success><Message.Header>{this.state.actionedmsg}</Message.Header></Message>
        )
      }
      else if(this.state.actionedmsg !== ''){
        return (
          <Message className="fullwidth" negative><Message.Header>{this.state.actionedmsg}</Message.Header></Message>        
        )
      }
  }
  
  generategriddefault(){
    if(this.state.inventory.length !== 0){
      
      return (
        <Card raised key="1">
          <Card.Content>
            <Image rounded
              centered src={this.state.defaultimage}
              floated='right'
              size='tiny'
            />
            <Card.Header size='tiny'>Add new item</Card.Header>
            <Card.Meta></Card.Meta>
            <Label color='grey' attached='top right'>0</Label>
          </Card.Content>

          <Card.Content extra textAlign="center">
            <Modal
              trigger={<Button icon="plus" onClick={this.openmodal} />}
              open={this.state.modalopen}
              onClose={this.closemodal} 
              centered={false}
              size="fullscreen"
              dimmer="blurring"
              >
              <Modal.Header>Add item to inventory</Modal.Header>
              <Modal.Content image>
                <Image wrapped size='tiny' src={this.state.productimage} />
                <Modal.Description>
                  <Grid columns={1} doubling stackable>
                    <Grid.Column>
                      <Dropdown className="fullwidth"
                        placeholder="Product name"
                        search
                        selection
                        noResultsMessage="No product found"
                        value={this.state.productname}
                        options={this.state.productsuggests}
                        onSearchChange={this.lookupproduct.bind(this)}
                        onChange={this.setinventorymetadata.bind(this)}
                      />
                    </Grid.Column>
                    <Grid.Column>
                      <Dropdown className="fullwidth"
                        placeholder="Retailer name"
                        search
                        selection
                        noResultsMessage="No retailer found"
                        value={this.state.retailername}
                        options={this.state.retailersuggests}
                        onSearchChange={this.lookupretailer.bind(this)}
                        onChange={this.setinventorymetadata.bind(this)}
                      />
                    </Grid.Column>
                    <Grid.Row columns={2}>
                      <Grid.Column>
                        <Input className="fullwidth"
                          placeholder='Quantity'
                          value={this.state.quantity}
                          onChange={this.setinventorymetadata.bind(this)}
                        />
                      </Grid.Column>
                      <Grid.Column>
                         <DateInput
                          placeholder="Expiry date"
                          dateFormat="YYYY-MM-DD"
                          value={this.state.dateexpiry}
                          onChange={this.setinventorymetadata.bind(this)}
                        />
                      </Grid.Column>
                    </Grid.Row>
                  </Grid>
                </Modal.Description>
              </Modal.Content>
              <Modal.Actions>
                <Grid columns={2} container doubling stackable>
                  <Grid.Column>
                    <Button loading={this.state.loading || false} className="fullwidth" color='black' onClick={this.addinventory.bind(this,this.state.gtin)}>
                      add
                    </Button>
                  </Grid.Column>
                  <Grid.Column>
                    {this.generateitemadditionmsg()}
                  </Grid.Column>
                </Grid>
              </Modal.Actions>
            </Modal>
          </Card.Content>
        </Card>
      )
    }
    else{
      return ''
    }
  }

  generategriditems(){
    if(this.state.inventory.length === 0){
      return (<Card raised>
                <Message warning size='tiny'
                  header="Fetching your inventory"
                  content="Please try again later if it doesn't load"
                />
              </Card>
              )
    }
    else{
      return _.map(this.state.inventory, (item) => (
              <Card raised key={item.gtin}>
                <Card.Content>
                    <Image rounded
                      centered src={item.productimage}
                      floated='right'
                      size='tiny' style={{width: 'auto', height: '70px'}}
                      onError={this.setdefaultimage.bind(this)}
                    />
                  <Card.Header size='tiny'>{item.productname}</Card.Header>
                  <Card.Meta>{item.brandname}</Card.Meta>
                  <Label color='grey' attached='top right'>{item.itemcount}</Label>
                </Card.Content>

                <Card.Content extra textAlign="center">
                  <div className='ui three buttons'>
                    <Button icon="edit" onClick={this.redirectoproduct.bind(this,item.gtin)} />
                    <Button icon="minus" onClick={this.consumeinventory.bind(this,item.gtin)}/>
                    <Modal
                      trigger={<Button icon="plus" />}
                      centered={false}
                      size="fullscreen"
                      dimmer="blurring"
                    >
                      <Modal.Header>Specify retailer, quantity and expiry</Modal.Header>
                      <Modal.Content image>
                        <Image wrapped size='tiny' src={item.productimage} />
                        <Modal.Description>
                          <Grid columns={1} doubling stackable>
                            <Grid.Column>
                              <Dropdown className="fullwidth"
                                placeholder="Retailer name"
                                search
                                selection
                                value={this.state.retailername}
                                options={this.state.retailersuggests}
                                onSearchChange={this.lookupretailer.bind(this)}
                                onChange={this.setinventorymetadata.bind(this)}
                              />
                            </Grid.Column>
                            <Grid.Row columns={2}>
                              <Grid.Column>
                                <Input className="fullwidth"
                                  placeholder='Quantity'
                                  value={this.state.quantity}
                                  onChange={this.setinventorymetadata.bind(this)}
                                />
                              </Grid.Column>
                              <Grid.Column>
                                 <DateInput
                                  placeholder="Expiry date"
                                  dateFormat="YYYY-MM-DD"
                                  value={this.state.dateexpiry}
                                  onChange={this.setinventorymetadata.bind(this)}
                                />
                              </Grid.Column>
                            </Grid.Row>
                          </Grid>
                        </Modal.Description>
                      </Modal.Content>
                      <Modal.Actions>
                        <Grid columns={2} container doubling stackable>
                          <Grid.Column>
                            <Button loading={this.state.loading || false} className="fullwidth" color="black" onClick={this.addinventory.bind(this,item.gtin)}>
                              add
                            </Button>
                          </Grid.Column>
                          <Grid.Column>
                            {this.generateitemadditionmsg()}
                          </Grid.Column>
                        </Grid>
                      </Modal.Actions>
                    </Modal>
                  </div>
                </Card.Content>
              </Card>
            ))
    }
  }

  render() {
    return (
      <Container fluid>
        <Card.Group doubling itemsPerRow={6} stackable>
          {this.generategriddefault()}
          {this.generategriditems()}
        </Card.Group>
      </Container>
    )
  }
}
export default Inventory;
