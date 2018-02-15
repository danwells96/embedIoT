package com.example.danwells.iotapp;

import android.app.Activity;
import android.content.Context;
import android.support.annotation.LayoutRes;
import android.support.annotation.NonNull;
import android.support.annotation.Nullable;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.Switch;
import android.widget.TextView;

/**
 * Created by danwells on 13/02/2018.
 */

public class MainAdapter extends ArrayAdapter {

    private final Activity contxt;
    private final String[] nameValues;

    public MainAdapter(@NonNull Activity context, @LayoutRes int resource, String[] nameData) {
        super(context, resource, nameData);
        this.contxt = context;
        this.nameValues = nameData;
    }

    @NonNull
    @Override
    public View getView(int position, @Nullable View convertView, @NonNull ViewGroup parent) {
        LayoutInflater inflater = contxt.getLayoutInflater();
        View rowView = inflater.inflate(R.layout.main_card, parent, false);
        TextView nameView = (TextView) rowView.findViewById(R.id.mainName);
        Switch status = (Switch) rowView.findViewById(R.id.statusSwitch);
        status.setId(position+1);
        nameView.setText(nameValues[position]);
        return rowView;
    }

    public void changeSwitch(int pos){
        Switch status = (Switch) contxt.findViewById(pos);
        if(status.isChecked()) {
            status.setChecked(false);
        }else{
            status.setChecked(true);
        }
    }

}
