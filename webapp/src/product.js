import React from 'react';
import axios from 'axios';
import {isMobile} from 'react-device-detect';
import { getToken } from './utils/common';
import { Checkbox, Card, Label, Message, Divider, Input, Dropdown, Grid, Button, Image } from 'semantic-ui-react'
import _ from 'lodash'

class Product extends React.Component {
  constructor(props) {
    super(props)
    const redirectstate = this.props.location.state;
    this.state = {
      //apihost: 'http://127.0.0.1:88',
      apihost: 'https://inven3s.xyz',
      token: getToken(),
      loading: false,
      actionedmsg: '',
      defaultimage: 'https://react.semantic-ui.com/images/wireframe/image.png',
      defaultcategoryoptions: [],
      productsuggests: [],
      brandsuggests: [],
      categorysuggests: [],
      productdropdown: '',
      gtin: redirectstate ? redirectstate.gtin : '',
      productname: redirectstate ? redirectstate.productname : '',
      productimage: redirectstate ? redirectstate.productimage : 'https://react.semantic-ui.com/images/wireframe/image.png',
      productimagelocal: redirectstate ? redirectstate.productimagelocal : 'https://react.semantic-ui.com/images/wireframe/image.png',
      brandname: redirectstate ? redirectstate.brandname : '',
      isedible: redirectstate ? redirectstate.isedible : 1,
      isperishable:0,
      selectedcategories: [],
      isfavourite: redirectstate ? redirectstate.isfavourite : 0,
      categoryoptions: redirectstate ? redirectstate.categoryoptions : []
    };
  }

  upsertproduct(event){
    this.setState({ actionedmsg: '' });
    this.setState({ loading: true });

    console.log('upsertproduct');

    if(this.state.productimage === this.state.defaultimage){
      this.setState({ productimage: '' });
    }

    axios.post(this.state.apihost + '/product', 
      {
        gtin:this.state.gtin,
        productname:this.state.productname,
        productimage:this.state.productimage,
        brandname:this.state.brandname,
        isedible:this.state.isedible,
        isperishable: this.state.isperishable,
        isfavourite: this.state.isfavourite,
        categories: this.state.selectedcategories
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
        console.log('upsertproduct [' + response.data[0]['message'] + ']');
        this.setState({ actionedmsg: response.data[0]['message'] });

        this.setState({ productname: response.data[0]['results'][0]['productname'] });
        this.setState({ productimage: response.data[0]['results'][0]['productimage'] });
        this.setState({ productimagelocal: response.data[0]['results'][0]['productimagelocal'] });
        this.setState({ brandname: response.data[0]['results'][0]['brandname'] });
        this.setState({ isedible: response.data[0]['results'][0]['isedible'] });
        this.setState({ isfavourite: response.data[0]['results'][0]['isfavourite'] });
        this.updatecategorysuggests(response.data[0]['results'][0]['categories']);
      }
      else{
        console.log('upsertproduct [' + response.data[0]['message'] + ']');
        this.setState({ actionedmsg: response.data[0]['message'] });        
      }
    })
    .catch(error => {
      this.setState({ loading: false });
      if(error.response){
        if(error.response.data){
          console.log('upsertproduct [' + error.response.status + ':' + error.response.data[0]['message'] + ']');
          this.setState({ actionedmsg: error.response.data[0]['message'] });        
        }
        else{
          console.log('upsertproduct [server unreachable]');
          this.setState({ actionedmsg: 'server unreachable' });
        }
      }
      else{
        console.log('upsertproduct [server unreachable]');
        this.setState({ actionedmsg: 'server unreachable' });
      }
    });
  }

  lookupproduct(event, data){
    const gtinorproduct = data.searchQuery

    if(gtinorproduct.length > 3){
      this.searchproducts(gtinorproduct);
    }
  }

  searchproducts(gtinorproduct){
    console.log('searchproducts [' + gtinorproduct + ']');

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
          console.log('searchproducts [' + response.data[0]['message'] + ']');
          
          this.updateproductsuggests(response.data[0]['results']);
        }
        else{
          console.log('searchproducts [' + response.data[0]['message'] + ']');          
        }
      })
      .catch(error => {
        if(error.response){
          if(error.response.data){
            console.log('searchproducts [' + error.response.status + ':' + error.response.data[0]['message'] + ']');
          }
          else{
            console.log('searchproducts [server unreachable]');
          }
        }
        else{
          console.log('searchproducts [server unreachable]');
        }
      });
  }

  updateproductsuggests(suggestions){
    const updatedsuggest = _.map(suggestions, (item) => (
        {
          key: item.gtin,
          text: item.productname,
          value: item.productname,
          img: item.productimage === '' ? this.state.defaultimage : item.productimage,
          imglocal: item.productimagelocal === '' ? this.state.defaultimage : item.productimagelocal,
          brand: item.brandname,
          isedible: item.isedible,
          isfavourite: item.isfavourite,
          categories: item.categories
        }
      ));
    this.setState({ productsuggests: updatedsuggest });
  }

  setproductmetadata(event, data){
    const field = data.name;
    const value = data.value;
    console.log('setproductmetadata [' + field + ':' + value + ']');

    if(field === 'productname'){
      const array = this.state.productsuggests;
      let selectedarr = [];

      try{
        selectedarr = array.filter(prod => prod.value.includes(value))[0];

        if(selectedarr){
          const selectedgtin = selectedarr['key'];
          const selectedimg = selectedarr['img'];
          const selectedimglocal = selectedarr['imglocal'];
          const selectedbrand = selectedarr['brand'];
          const selectedisedible = selectedarr['isedible'];
          const selectedisfavourite = selectedarr['isfavourite'];
          const selectedprodcategoryoptions = selectedarr['categories'];

          this.setState({ productdropdown: value });
          this.setState({ gtin: selectedgtin });
          this.setState({ productname: value });
          this.setState({ productimage: selectedimg });
          this.setState({ productimagelocal: selectedimglocal });
          this.setState({ brandname: selectedbrand });
          this.setState({ isedible: selectedisedible });
          this.setState({ isfavourite: selectedisfavourite });
          this.setState({ categoryoptions: selectedprodcategoryoptions });
          
          this.searchbrands(selectedbrand,0);

          if(selectedprodcategoryoptions.length > 0){
            this.updatecategorysuggests(selectedprodcategoryoptions);
          }
          else{//LOAD DEFAULT CATS IF NOT CATS PREDICTED FOR PRODUCT YET
            this.setState({ categorysuggests: this.state.defaultcategoryoptions });
            this.setState({ selectedcategories: [] });
          }
        }
        else{
          //NEW PRODUCT
        }
      }
      catch(error){
        console.log("setproductmetadata: " + error)
      }
    }
    else if(field === 'brandname'){
      const array = this.state.brandsuggests;
      let selectedarr = array.filter(brand => brand.value.includes(value))[0];
      if(selectedarr){
        const brandid = selectedarr['key'];

        this.setState({ brandid: brandid });
        this.setState({ brandname: value });
      }
      else{
        //NEW BRAND
      }
    }
    else if(field === 'categoryname'){
      this.setState({ selectedcategories: value });
    }    
  }

  addnewbrand(event,data){
    this.setState({ actionedmsg: '' });
    this.setState({ loading: true });

    const newbrand = data.value;
    console.log('addnewbrand [' + newbrand + ']');

    axios.post(this.state.apihost + '/brand', 
      {
        brandid:'',
        brandname:newbrand,
        brandimage:'',
        brandurl:'',
        brandowner:''
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
        console.log('addnewbrand [' + response.data[0]['message'] + ']');
        this.setState({ actionedmsg: response.data[0]['message'] }); 

        this.setState({ brandid: response.data[0]['results'][0]['brandid'] });
        this.setState({ brandname: response.data[0]['results'][0]['brandname'] });
      }
      else{
        console.log('addnewbrand [' + response.data[0]['message'] + ']');
        this.setState({ actionedmsg: response.data[0]['message'] });                
      }
    })
    .catch(error => {
      this.setState({ loading: false });
      if(error.response){
        if(error.response.data){
          console.log('addnewbrand [' + error.response.status + ':' + error.response.data[0]['message'] + ']');
          this.setState({ actionedmsg: error.response.data[0]['message'] });        
        }
        else{
          console.log('addnewbrand [server unreachable]');
          this.setState({ actionedmsg: 'server unreachable' });        
        }
      }
      else{
        console.log('addnewbrand [server unreachable]');
        this.setState({ actionedmsg: 'server unreachable' });        
      }
    });    
  }

  addnewproduct(event,data){
    this.setState({ actionedmsg: '' });
    this.setState({ loading: true });

    const gtincandidate = data.value;
    console.log('addnewproduct [' + gtincandidate + ']');
    
    axios.get(this.state.apihost + '/product/discover/' + gtincandidate,
        {
          headers: {
            "content-type": "application/json",
            "access-token": this.state.token
          }
        }
      )
      .then(response => { 
        this.setState({ loading: false });
        if(response.status === 200){
          console.log('addnewproduct [' + response.data[0]['message'] + ']');
          this.setState({ actionedmsg: response.data[0]['message'] });

          const newproductdata = response.data[0]['results'][0]
          this.setState({ productdropdown: newproductdata['productname'] });
          this.setState({ gtin: newproductdata['gtin'] });
          this.setState({ productname: newproductdata['productname'] });
          this.setState({ productimage: newproductdata['productimage'] });
          this.setState({ productimagelocal: newproductdata['productimagelocal'] });
          this.setState({ brandname: newproductdata['brandname'] });
          this.setState({ isedible: newproductdata['isedible'] });
          this.setState({ isfavourite: newproductdata['isfavourite'] });

          this.searchbrands(newproductdata['brandname'],0);

          if(newproductdata['categories'].length > 0){
            this.updatecategorysuggests(newproductdata['categories']);
          }
          else{//LOAD DEFAULT CATS IF NOT CATS PREDICTED FOR PRODUCT YET
            this.setState({ categorysuggests: this.state.defaultcategoryoptions });
            this.setState({ selectedcategories: [] });
          }
        }
        else{
          console.log('addnewproduct [' + response.data[0]['message'] + ']');
          this.setState({ actionedmsg: response.data[0]['message'] });                
        }
      })
      .catch(error => {
        this.setState({ loading: false });
        this.setState({ gtin: gtincandidate});//STILL WANT TO ALLOW USERS TO ADD PRODUCT THAT CANT BE DISCOVEDED FROM WEB
        if(error.response){
          if(error.response.data){
            console.log('addnewproduct [' + error.response.status + ':' + error.response.data[0]['message'] + ']');
            this.setState({ actionedmsg: error.response.data[0]['message'] });        
          }
          else{
            console.log('addnewproduct [server unreachable]');
            this.setState({ actionedmsg: 'server unreachable' });        
          }
        }
        else{
          console.log('addnewproduct [server unreachable]');
          this.setState({ actionedmsg: 'server unreachable' });        
        }
      });
  }

  updatecategorysuggests(suggestions){
    const updatedsuggest = _.map(suggestions, (cat) => (
        {
          key: cat.name,
          text: cat.name,
          value: cat.name,
          status: cat.status,
          confidence: cat.confidence
        }
      ));
    this.setState({ categorysuggests: updatedsuggest });
    let selectedcats = [];
    suggestions.forEach(function(cat) {
      if(cat.status === 'SELECTED'){
        selectedcats.push(cat.name);
      }
    });  
    this.setState({ selectedcategories: selectedcats });
  }  

  updatebrandsuggests(suggestions){
    const updatedsuggest = _.map(suggestions, (item) => (
        {
          key: item.brandid,
          text: item.brandname,
          value: item.brandname,
        }
      ));
    this.setState({ brandsuggests: updatedsuggest });
  }  

  lookupbrand(event, data){
    const brand = data.searchQuery;

    if(brand.length > 1){
      this.searchbrands(brand,0);
    }
  }

  fetchdefaultcategories(){
    console.log('fetchdefaultcategories');

    axios.get(this.state.apihost + '/category',
        {
          headers: {
            "content-type": "application/json",
            "access-token": this.state.token
          }
        }
      )
      .then(response => { 
        if(response.status === 200){
          console.log('fetchdefaultcategories [' + response.data[0]['message'] + ']');
          this.updatedefaultcategories(response.data[0]['results']);
        }
        else{
          console.log('fetchdefaultcategories [' + response.data[0]['message'] + ']');
        }
      })
      .catch(error => {
        console.log('fetchdefaultcategories [server unreachable]');
      });
  }

  searchbrands(brand,preloaddefaultcatafter){
    console.log('searchbrands [' + brand + ']');

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
          console.log('searchbrands [' + response.data[0]['message'] + ']');
          this.updatebrandsuggests(response.data[0]['results']);
          
          if(preloaddefaultcatafter === 1){
            this.fetchdefaultcategories();
          }
        }
        else{
          console.log('searchbrands [' + response.data[0]['message'] + ']');
        }
      })
      .catch(error => {
        if(error.response){
          if(error.response.data){
            console.log('searchbrands [' + error.response.status + ':' + error.response.data[0]['message'] + ']');
          }
          else{
            console.log('searchbrands [server unreachable]');
          }
        }
        else{
          console.log('searchbrands [server unreachable]');
        }
      });
  }

  updatedefaultcategories(defaultcats){
    const updatedsuggest = _.map(defaultcats, (cat) => (
        {
          key: cat.category,
          text: cat.category,
          value: cat.category,
          status: 'SELECTED',
          confidence: cat.count
        }
      ));
    this.setState({ defaultcategoryoptions: updatedsuggest });
    this.setState({ categorysuggests: updatedsuggest });
  }

  updateedibletoggle(event,data){
    if(data.checked){
      this.setState({ isedible: 1 });
    }
    else{
      this.setState({ isedible: 0 });
    }
  }

  updatefavouritetoggle(event,data){
    if(data.checked){
      this.setState({ isfavourite: 1 });
    }
    else{
      this.setState({ isfavourite: 0 });
    }
  }

  generateitemadditionmsg(){
    if(this.state.actionedmsg !== ''){
      return (
        <Message className="fullwidth" size="tiny">{this.state.actionedmsg}</Message>
      )
    }
  }

  componentDidMount() {
    //ONLOAD, IF REDIRECT WITH PRODUCT DETAILS FROM INVENTORY. NEED TO POPULATE DROPDOWN
    
    if(this.state.brandname !== ''){
      this.searchbrands(this.state.brandname,1);//PRELOAD DEFAULT CAT === 1
    }
    else{//IF NO BRANDS, WE'LL LOAD DEFAULT CAT SEPARATELY
      this.fetchdefaultcategories();
    }

    if(this.state.categoryoptions.length > 0){
      this.updatecategorysuggests(this.state.categoryoptions);
    }
  }

  checkfavourite(){
    if(this.state.isfavourite === 1){
      return true;
    }
    else{
      return false;
    }
  }

  checkedible(){
    if(this.state.isedible === 1){
      return true;
    }
    else{
      return false;
    }
  }

  render() {
    return (
      <div
        className={isMobile ? "bodymain mobile" : "bodymain"}
      >
        <Card raised fluid>
          <Card.Content>
            <Card.Description>
              <Grid columns={1} doubling stackable>
                <Grid.Column>
                  <Dropdown className="fullwidth" name="productname"
                      search
                      selection
                      allowAdditions
                      value={this.state.productdropdown}
                      options={this.state.productsuggests}
                      additionLabel = "Add new product "
                      noResultsMessage = "No product found"
                      onSearchChange={this.lookupproduct.bind(this)}
                      onAddItem={this.addnewproduct.bind(this)}
                      onChange={this.setproductmetadata.bind(this)}
                  />
                </Grid.Column>
              </Grid>
            </Card.Description>
            <Divider/>
            <Card.Meta>
              <Grid columns={1} doubling stackable>
                <Grid.Row columns={2}>
                  <Grid.Column width={4}>
                    <Image inline
                      src={this.state.productimagelocal}
                      size="small"
                      spaced="left"
                      onError={(e)=>{e.target.onerror = null; e.target.src=this.state.productimage}}
                    />
                  </Grid.Column>
                  <Grid.Column width={11}>
                    <label className="fullwidth">GTIN</label>
                    <Input className="fullwidth" disabled value={this.state.gtin}/>
                  </Grid.Column>
                </Grid.Row>
                <Grid.Column>
                  <label className="fullwidth">Product</label>
                  <Input value={this.state.productname} className="fullwidth" onChange={e => this.setState({ productname: e.target.value })}/>
                </Grid.Column>
                <Grid.Column>
                  <label className="fullwidth">Image</label>
                  <Input value={this.state.productimage} className="fullwidth" onChange={e => this.setState({ productimage: e.target.value })}/>                     
                </Grid.Column>
                <Grid.Row columns={2}>
                  <Grid.Column width={5}>
                    <label className="fullwidth">Brand</label>
                    <Dropdown className="fullwidth" name="brandname" 
                      search
                      selection
                      allowAdditions
                      value={this.state.brandname}
                      options={this.state.brandsuggests}
                      additionLabel = "Add new brand "
                      noResultsMessage = "No brand found"
                      onSearchChange={this.lookupbrand.bind(this)}
                      onAddItem={this.addnewbrand.bind(this)}
                      onChange={this.setproductmetadata.bind(this)}
                    />
                  </Grid.Column>
                  <Grid.Column width={10}>
                    <label className="fullwidth">Category</label>
                    <Dropdown className="fullwidth" name="categoryname"
                      clearable
                      multiple
                      search
                      selection
                      value={this.state.selectedcategories}
                      options={this.state.categorysuggests}
                      onChange={this.setproductmetadata.bind(this)}
                    />
                  </Grid.Column>
                </Grid.Row>
                <Grid.Column>
                   <Checkbox toggle label='Is edible?' checked={this.checkedible()} onChange={this.updateedibletoggle.bind(this)}/>
                   <Checkbox toggle label='Is favourite?' checked={this.checkfavourite()} onChange={this.updatefavouritetoggle.bind(this)}/>
                </Grid.Column>
              </Grid>
            </Card.Meta>
            <Label className='grey button' attached='top right'>0</Label>
          </Card.Content>
          <Card.Content extra textAlign="center">
            <Grid columns={2} doubling stackable>
              <Grid.Column>
                <Button loading={this.state.loading || false}
                className='grey button fullwidth' onClick={this.upsertproduct.bind(this)}>
                  ADD OR UPDATE
                </Button>
              </Grid.Column>
              <Grid.Column>
                {this.generateitemadditionmsg()}
              </Grid.Column>
            </Grid>
          </Card.Content>
        </Card>
      </div>
    )
  }
}
export default Product;

