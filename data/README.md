# Data Directory

## Required Data Format

Place your Facebook Ads performance data in `sample_fb_ads.csv` with the following columns:

### Required Columns

- **campaign_name** (string): Name of the advertising campaign
- **creative_message** (string): The ad creative text/message
- **roas** (float): Return on Ad Spend - revenue generated per dollar spent
- **ctr** (float): Click-Through Rate - percentage of impressions that resulted in clicks
- **spend** (float): Total amount spent on the campaign/ad set
- **impressions** (integer): Number of times the ad was shown
- **clicks** (integer): Number of times users clicked on the ad
- **date** (string): Date of the record in YYYY-MM-DD format

### Optional Columns

- **campaign_id**: Unique campaign identifier
- **adset_name**: Ad set name
- **audience**: Target audience description
- **objective**: Campaign objective (conversions, traffic, etc.)
- **platform**: Platform where the ad ran (Facebook, Instagram, etc.)

## Sample Data

The system will automatically generate sample data if no CSV file is found.

## Example CSV Structure

```csv
campaign_name,creative_message,roas,ctr,spend,impressions,clicks,date
Summer Sale,Get 40% off on all items! Shop now,3.5,0.035,250.0,5000,175,2024-01-15
Summer Sale,Don't miss our summer deals!,2.8,0.028,180.0,3200,90,2024-01-16
Winter Collection,Cozy winter essentials up to 50% off,4.2,0.042,320.0,4500,189,2024-01-20
```

## Notes

- Date format should be consistent (YYYY-MM-DD recommended)
- ROAS values typically range from 1.0 to 10.0+
- CTR values are typically between 0.01 (1%) and 0.10 (10%)
- The system will analyze all campaigns in the dataset
- More data (more rows) = better insights


